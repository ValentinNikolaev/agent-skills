"""Offline, single-project DAG runner. Every successful operation appends a checkpoint."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

from contracts import Invalid, acyclic, check_bundle, load, require, resources, text_value, unique_index


PRESETS = Path(__file__).resolve().parents[1] / "references" / "presets.json"
GATES = {"contract", "intake-audit", "review", "alignment-review"}


def new_plan(project, specs):
    require(text_value(project), "missing project identifier")
    contracts = load(resources() / "contracts.json")["artifacts"]
    nodes = unique_index(specs, "nodes")
    require(nodes, "empty workflow")
    for node in nodes.values():
        after = node.get("after")
        require(isinstance(after, list) and all(text_value(p) and p in nodes for p in after),
                f"{node['id']}: unresolved prerequisite")
        outputs = node.get("outputs")
        require(isinstance(outputs, list) and outputs and all(k in contracts for k in outputs),
                f"{node['id']}: unknown output")
        owners = {o for spec in contracts.values() for o in spec["owners"] if o not in ("*", "caller", "importer")}
        require(node.get("skill") in owners and all(node["skill"] in contracts[k]["owners"]
                or "*" in contracts[k]["owners"] for k in outputs), f"{node['id']}: wrong specialist")
        require(node.get("gate") in GATES, "unknown quality gate")
        if node["gate"] in ("review", "alignment-review", "intake-audit"):
            require("ReviewReport" in outputs and not node.get("optional"), "review gate must be mandatory")
    acyclic({key: n["after"] for key, n in nodes.items()}, "workflow")
    state = {"schema_version": 1, "project": project, "sequence": 0, "nodes": copy.deepcopy(nodes),
             "log": [{"event": "init"}], "versions": {}}
    for node in state["nodes"].values():
        node.update(status="pending", attempts=0, reason=None, artifacts={})
    readiness(state)
    return state


def readiness(state):
    nodes = state["nodes"]
    for node in nodes.values():
        if node["status"] in ("pending", "ready"):
            done = all(nodes[p]["status"] in ("passed", "skipped") for p in node["after"])
            node["status"] = "ready" if done else "pending"


def invalidate(state, roots):
    nodes = state["nodes"]
    affected = set(roots)
    for key in acyclic({k: n["after"] for k, n in nodes.items()}, "workflow"):
        node = nodes[key]
        if any(p in affected for p in node["after"]):
            affected.add(key)
        if key in affected:
            node.update(status="stale", reason="input or scope changed")
    return sorted(affected)


def digest(value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def input_stamps(bundle, pinned):
    # Fingerprint the transitive inputs as well as the output. Keep raw learner data out of the journal.
    sources = unique_index(bundle.get("sources", []), "sources")
    base = load(resources() / "evidence.json")
    for row in base["sources"] + base["rules"]:
        sources[row["id"]] = row
    def strings(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for child in value.values():
                yield from strings(child)
        elif isinstance(value, list):
            for child in value:
                yield from strings(child)
    stamps = {}
    for ref in acyclic({r: a["depends_on"] for r, a in pinned.items()}, "artifacts"):
        artifact = pinned[ref]
        used = sorted(set(strings(artifact["data"])).intersection(sources))
        stamps[ref] = digest([artifact, [stamps[d] for d in artifact["depends_on"]], [sources[s] for s in used]])
    return stamps


def audit_retests(nodes, node, outputs, targets):
    """Carry blocking intake findings across superseded private artifact snapshots."""
    upstream = set(node["after"])
    for key in reversed(acyclic({k: n["after"] for k, n in nodes.items()}, "workflow")):
        if key in upstream:
            upstream.update(nodes[key]["after"])
    required = {finding for key in upstream for finding in nodes[key].get("blocking_findings", [])}
    verified = set()
    for report in outputs:
        for record in report["data"].get("retests", []):
            require(isinstance(record, dict) and record.get("target") in targets
                    and text_value(record.get("evidence")), "retest must identify current target and observed result")
            verified.add(record.get("finding"))
    require(required <= verified, f"intake findings still need a retest: {sorted(required - verified)}")


def advance(previous, action, node_id=None, *, bundle=None, refs=(), reason=None):
    state = copy.deepcopy(previous)
    nodes = state["nodes"]
    require(action == "refresh" or node_id in nodes, "unknown node")
    pinned = check_bundle(bundle) if bundle is not None else {}
    stamps = input_stamps(bundle, pinned) if bundle is not None else {}
    # An accepted artifact is immutable at a given revision across this project.
    for ref, artifact in pinned.items():
        known = state["versions"].get(ref)
        require(known is None or known == digest(artifact), f"{ref}: edits require a new revision")
    event = {"event": action, "node": node_id}
    node = nodes.get(node_id)
    if action == "refresh":
        require(bundle is not None, "refresh requires the current complete project bundle")
        changed = {k for k, n in nodes.items() if n["status"] == "passed" and n["gate"] != "intake-audit" and any(
            stamps.get(ref) != stamp for ref, stamp in n["artifacts"].items())}
        event["affected"] = invalidate(state, changed)
    elif action == "reopen":
        require(node["status"] in ("passed", "running", "skipped"), "only active or accepted work can be reopened")
        require(text_value(reason), "record the scope change or revision reason")
        event["affected"] = invalidate(state, [node_id])
    elif action == "start":
        require(node["status"] in ("ready", "failed", "stale", "blocked"), "node cannot start in this state")
        require(all(nodes[p]["status"] in ("passed", "skipped") for p in node["after"]), "upstream work incomplete")
        require(node["attempts"] < 3, "attempt limit reached; record a changed plan and retain this history")
        if node["status"] in ("failed", "blocked"):
            require(text_value(reason), "record what changed before retrying")
        node.update(status="running", attempts=node["attempts"] + 1, reason=None)
    elif action in ("fail", "block", "skip"):
        require(text_value(reason), "record a reason")
        if action == "skip":
            require(node.get("optional") is True and node["status"] in ("pending", "ready", "stale"),
                    "only an optional unstarted branch can be skipped")
            node["status"] = "skipped"
        elif action == "block":
            require(node["status"] in ("pending", "ready", "running", "stale"), "invalid block")
            node["status"] = "blocked"
        else:
            require(node["status"] == "running", "only a running node can fail")
            node["status"] = "failed"
        node["reason"] = reason
    elif action == "pass":
        require(node["status"] == "running", "only a running node can pass")
        require(bundle is not None and refs and len(set(refs)) == len(refs) and all(r in pinned for r in refs),
                "return verified artifact revisions")
        outputs = [pinned[r] for r in refs]
        require({a["kind"] for a in outputs} == set(node["outputs"]), "incomplete or unexpected output kinds")
        require(all(a["producer"] == node["skill"] and a["status"] != "draft" for a in outputs),
                "draft or wrong-owner stage output")
        parents = [nodes[p] for p in node["after"] if nodes[p]["status"] == "passed"]
        for parent in parents:
            if parent["gate"] == "intake-audit":
                continue  # Its frozen report describes the superseded input snapshot.
            require(all(stamps.get(r) == v for r, v in parent["artifacts"].items()),
                    f"{parent['id']}: stale or missing parent output; refresh before accepting")
        if node["gate"] == "intake-audit":
            node["blocking_findings"] = [
                f"{ref}#{index}" for ref in refs for index, finding in enumerate(pinned[ref]["data"]["findings"], 1)
                if finding["severity"] in ("critical", "high") and finding["status"] != "fixed"]
            for ref in refs:
                report = pinned[ref]["data"]
                require(report["decision"] == "pass" or report["findings"],
                        "a rejected intake needs located findings for remediation")
        if node["gate"] in ("review", "alignment-review"):
            targets = {r for a in outputs if a["kind"] == "ReviewReport" for r in a["data"]["targets"]}
            expected = {r for p in parents for r in p["artifacts"]}
            require(expected <= targets, "review does not cover the current parent outputs")
            require(all(a["data"]["decision"] == "pass" for a in outputs if a["kind"] == "ReviewReport"),
                    "review blocked or requires revision")
            audit_retests(nodes, node, outputs, targets)
            if node["gate"] == "alignment-review":
                check_bundle(bundle, alignment=True, reviewed=targets)
            if node.get("high_stakes") or any(a["kind"] == "ProjectBrief" and a["data"].get("stakes") == "high"
                                              for a in pinned.values()):
                for report in outputs:
                    approval = report["data"].get("qualified_approval", {})
                    require(isinstance(approval, dict) and all(text_value(approval.get(k))
                            for k in ("reviewer_role", "decision_record", "date")),
                            "qualified human approval record required for high-stakes use")
        node.update(status="passed", reason=None, artifacts={r: stamps[r] for r in refs})
        # Preserve hashes for input revisions as well as produced revisions.
        used = set(refs)
        for ref in reversed(acyclic({r: a["depends_on"] for r, a in pinned.items()}, "artifacts")):
            if ref in used:
                used.update(pinned[ref]["depends_on"])
        state["versions"].update({r: digest(pinned[r]) for r in used})
        event["artifacts"] = list(refs)
    else:
        raise Invalid(f"unknown action {action}")
    if reason:
        event["reason"] = reason
    state["sequence"] += 1
    state["log"].append(event)
    readiness(state)
    return state


def save(directory, state):
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"checkpoint-{state['sequence']:08d}.json"
    # Atomic create-if-absent: a concurrent command based on the same snapshot loses cleanly.
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=directory, delete=False) as temp:
        temp_path = Path(temp.name)
        try:
            json.dump(state, temp, indent=2, ensure_ascii=False)
            temp.flush()
            os.fsync(temp.fileno())
        except BaseException:
            temp.close()
            temp_path.unlink(missing_ok=True)
            raise
    try:
        os.link(temp_path, target)
    finally:
        temp_path.unlink(missing_ok=True)
    return target


def latest(directory):
    files = sorted(directory.glob("checkpoint-*.json"))
    require(files, "no checkpoint; initialise this project first")
    state = load(files[-1])
    require(state.get("schema_version") == 1 and isinstance(state.get("nodes"), dict),
            "incompatible checkpoint")
    return state


def inventory(bundle):
    """Export only predefined material types and counts, without project-provided strings."""
    pinned = check_bundle(bundle)
    public_kinds = ("LearningMaterial", "LearningObjective", "AssessmentBlueprint", "AssessmentItem")
    return {kind: sum(a["kind"] == kind for a in pinned.values()) for kind in public_kinds}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    check = commands.add_parser("check")
    check.add_argument("bundle", type=Path)
    check.add_argument("--alignment", action="store_true")
    summary = commands.add_parser("inventory", help="print material counts without learner records")
    summary.add_argument("bundle", type=Path)
    for action in ("init", "status", "refresh", "start", "pass", "fail", "block", "skip", "reopen"):
        sub = commands.add_parser(action)
        sub.add_argument("journal", type=Path)
        if action == "init":
            group = sub.add_mutually_exclusive_group(required=True)
            group.add_argument("--preset", choices=tuple(load(PRESETS)))
            group.add_argument("--plan", type=Path)
            sub.add_argument("--project", required=True)
        if action not in ("init", "status", "refresh"):
            sub.add_argument("node")
            sub.add_argument("--reason")
        if action in ("refresh", "pass"):
            sub.add_argument("--bundle", type=Path, required=True)
        if action == "pass":
            sub.add_argument("refs", nargs="+")
    args = parser.parse_args()
    if args.action == "inventory":
        print(json.dumps(inventory(load(args.bundle))))
        return
    if args.action == "check":
        print(f"validated {len(check_bundle(load(args.bundle), args.alignment))} artifact revisions")
        return
    if args.action == "init":
        specs = load(args.plan) if args.plan else load(PRESETS)[args.preset]
        state = new_plan(args.project, specs)
    else:
        state = latest(args.journal)
        if args.action == "status":
            for key, n in state["nodes"].items():
                print(key, n["status"], n["reason"] or "", " ".join(n["artifacts"]))
            return
        bundle = load(args.bundle) if hasattr(args, "bundle") else None
        state = advance(state, args.action, getattr(args, "node", None), bundle=bundle,
                        refs=getattr(args, "refs", ()), reason=getattr(args, "reason", None))
    print(save(args.journal, state))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        sys.exit(f"education workflow: {exc}")
