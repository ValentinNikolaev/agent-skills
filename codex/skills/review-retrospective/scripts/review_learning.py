#!/usr/bin/env python3
"""Prepare review evidence or local model decisions; read JSON, print JSON only."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timedelta
import hashlib
import json
import math
from pathlib import Path
import sys

SKILLS = {"code-review", "plan-review", "review-arch"}
KINDS = {"missed-defect", "false-positive", "severity", "verdict", "cost", "clean-control"}
STATUSES = {"verified", "unverified", "disputed"}
PROPOSAL_FIELDS = ("skill", "stage", "risk_scope", "from_model", "to_model", "to_reasoning")


def mapping(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def sequence(value, label):
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def versioned(value):
    mapping(value, "input")
    if type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise ValueError("schema_version must be 1")
    return value


def number(value, label, maximum=None, integer=False):
    if value is None:
        return None
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < 0
            or (maximum is not None and value > maximum)
            or (integer and not isinstance(value, int))):
        raise ValueError(f"invalid {label}")
    return value


def instant(value):
    parsed = datetime.fromisoformat(text(value, "timestamp").replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone")
    return parsed


def normalize_cost(run):
    raw = mapping(run.get("usage", {}), "usage")
    usage = {key: number(raw.get(key), key, integer=True) for key in (
        "input_tokens", "output_tokens", "cached_input_tokens", "reasoning_tokens", "model_calls")}
    for subset, total in (("cached_input_tokens", "input_tokens"), ("reasoning_tokens", "output_tokens")):
        if usage[subset] is not None and usage[total] is not None and usage[subset] > usage[total]:
            raise ValueError(f"{subset} exceeds {total}")
    usage["total_tokens"] = (usage["input_tokens"] + usage["output_tokens"]
                             if usage["input_tokens"] is not None and usage["output_tokens"] is not None
                             else None)
    raw_time = mapping(run.get("timing", {}), "timing")
    timing = {key: number(raw_time.get(key), key) for key in (
        "elapsed_seconds", "waiting_seconds", "active_seconds")}
    measured = [timing[key] for key in ("waiting_seconds", "active_seconds") if timing[key] is not None]
    if timing["elapsed_seconds"] is not None and sum(measured) > timing["elapsed_seconds"]:
        raise ValueError("active/waiting time exceeds elapsed time")
    limits = []
    for item in sequence(run.get("limit_usage", []), "limit_usage"):
        item = mapping(item, "limit snapshot")
        kind = item.get("kind")
        if kind not in {"subscription", "context", "stage-budget"}:
            raise ValueError("invalid limit kind")
        window = text(item.get("window"), "limit window")
        source = text(item.get("source"), "limit source")
        before = number(item.get("before_percent"), "before_percent", 100)
        after = number(item.get("after_percent"), "after_percent", 100)
        exclusive = item.get("exclusive", False)
        if not isinstance(exclusive, bool):
            raise ValueError("exclusive must be boolean")
        same_window = (isinstance(item.get("before_window_id"), str)
                       and bool(item["before_window_id"].strip())
                       and item["before_window_id"] == item.get("after_window_id"))
        comparable = before is not None and after is not None and same_window and after >= before
        delta = after - before if comparable else None
        limits.append({"kind": kind, "window": window, "source": source,
                       "before_percent": before, "after_percent": after,
                       "observed_delta_pp": delta,
                       "review_delta_pp": delta if exclusive else None,
                       "limit": ("missing/reset snapshot" if not comparable else
                                 "shared or unknown attribution" if not exclusive else None)})
    return {"usage": usage, "timing": timing, "limit_usage": limits}


def upstream_checks(run, lookup):
    if run["skill"] != "code-review":
        return []
    supplied = {}
    for item in sequence(run.get("upstream", []), "upstream"):
        item = mapping(item, "upstream entry")
        skill = item.get("skill")
        if skill not in {"plan-review", "review-arch"} or skill in supplied:
            raise ValueError("invalid or duplicate upstream skill")
        if not isinstance(item.get("invoked"), bool):
            raise ValueError("upstream invoked must be boolean")
        supplied[skill] = item
    result = []
    for skill in ("plan-review", "review-arch"):
        item = supplied.get(skill)
        other = lookup.get(item.get("run_id")) if item else None
        if item is None:
            status = "skipped-invocation-unknown"
        elif not item["invoked"]:
            status = "skipped-not-invoked"
        elif not item.get("invocation_evidence") or other is None:
            status = "unavailable"
        elif other.get("task_id") != run["task_id"] or other.get("skill") != skill:
            status = "scope-mismatch"
        elif any(not other.get(key) or other[key] == "unknown" for key in (
                "input_artifact", "report_artifact", "input_revision")):
            status = "unavailable"
        else:
            status = "eligible"
        result.append({"run_id": run["run_id"], "skill": skill,
                       "upstream_run_id": item.get("run_id") if item else None, "status": status})
    return result


def prepare(document, task, max_cases=5):
    versioned(document)
    text(task, "task")
    if type(max_cases) is not int or max_cases < 1:
        raise ValueError("max_cases must be a positive integer")
    lookup = {}
    for raw in sequence(document.get("runs"), "runs"):
        run = mapping(raw, "run")
        run_id = text(run.get("run_id"), "run_id")
        if run_id in lookup:
            raise ValueError("duplicate run_id")
        lookup[run_id] = run
    selected = [run for run in lookup.values() if run.get("task_id") == task]
    if not selected:
        raise ValueError("no runs for requested task")
    cases, records, checks = [], [], []
    assessed = 0
    for run in selected:
        if run.get("skill") not in SKILLS:
            raise ValueError("unsupported review skill")
        record = {key: run.get(key, "unknown") for key in (
            "run_id", "task_id", "skill", "skill_revision", "input_revision",
            "input_artifact", "report_artifact", "model", "mode")}
        record.update({key: deepcopy(run.get(key)) for key in (
            "stage", "scope", "outcome", "coverage_limits", "captured_at")})
        records.append({**record, **normalize_cost(run)})
        checks.extend(upstream_checks(run, lookup))
        event_ids = set()
        for raw in sequence(run.get("feedback", []), "feedback"):
            event = mapping(raw, "feedback event")
            event_id = text(event.get("event_id"), "event_id")
            if event_id in event_ids:
                raise ValueError("duplicate event_id within run")
            event_ids.add(event_id)
            revision = text(event.get("evidence_revision"), "evidence_revision")
            text(event.get("evidence"), "evidence")
            if event.get("kind") not in KINDS or event.get("status") not in STATUSES:
                raise ValueError("invalid feedback kind/status")
            priority = event.get("priority", "P2")
            if priority not in {"P0", "P1", "P2", "P3"}:
                raise ValueError("invalid feedback priority")
            if event.get("assessed_revision") == revision:
                assessed += 1
                continue
            cases.append({**deepcopy(event), "priority": priority, "run_id": run["run_id"]})
    cases.sort(key=lambda event: int(event["priority"][1]))
    return {"schema_version": 1, "task_id": task, "runs": records,
            "cases": cases[:max_cases], "deferred_count": max(0, len(cases) - max_cases),
            "already_assessed_count": assessed, "upstream_checks": checks}


def policy_parts(envelope):
    mapping(envelope, "envelope")
    policy = versioned(envelope.get("policy"))
    mapping(policy.get("defaults", {}), "defaults")
    decisions = mapping(policy.get("decisions", {}), "decisions")
    proposal = mapping(envelope.get("proposal"), "proposal")
    fields = [text(proposal.get(key), key) for key in PROPOSAL_FIELDS]
    if proposal["skill"] not in SKILLS:
        raise ValueError("unsupported proposal skill")
    key = hashlib.sha256(json.dumps(fields, ensure_ascii=True).encode()).hexdigest()
    scope_key = hashlib.sha256(json.dumps(fields[:3], ensure_ascii=True).encode()).hexdigest()
    for entry in decisions.values():
        mapping(entry, "decision")
        if entry.get("status") not in {"accepted", "declined-pending", "deferred", "dismissed", "reminded"}:
            raise ValueError("invalid saved decision status")
    return policy, proposal, key, scope_key


def offer(envelope, at):
    _, _, key, _ = policy_parts(envelope)
    now = instant(at)
    entry = envelope["policy"].get("decisions", {}).get(key)
    if entry is None:
        return {"eligible": True, "reason": "new-proposal", "proposal_key": key}
    status = entry["status"]
    due = status == "deferred" and now >= instant(entry.get("remind_at"))
    return {"eligible": due, "reason": "one-reminder-due" if due else status, "proposal_key": key}


def decide(envelope, action, at):
    policy, proposal, key, scope_key = policy_parts(envelope)
    now = instant(at)
    updated = deepcopy(policy)
    decisions = updated.setdefault("decisions", {})
    entry = {"proposal": deepcopy(proposal), "updated_at": now.isoformat()}
    if action == "accept":
        entry["status"] = "accepted"
        updated.setdefault("defaults", {})[scope_key] = {
            "skill": proposal["skill"], "stage": proposal["stage"],
            "risk_scope": proposal["risk_scope"], "model": proposal["to_model"],
            "reasoning": proposal["to_reasoning"], "accepted_at": now.isoformat(), "proposal_key": key}
    elif action == "decline":
        entry["status"] = "declined-pending"
    elif action == "remind-week":
        entry.update(status="deferred", remind_at=(now + timedelta(days=7)).isoformat())
    elif action == "never":
        entry["status"] = "dismissed"
    elif action == "reminder-shown":
        if offer(envelope, at)["reason"] != "one-reminder-due":
            raise ValueError("no reminder is due")
        entry.update(status="reminded", reminder_shown_at=now.isoformat())
    else:
        raise ValueError("invalid decision action")
    decisions[key] = entry
    return updated


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "offer", "decision"):
        command = commands.add_parser(name)
        command.add_argument("--input", required=True, help="JSON path or - for stdin")
        if name == "prepare":
            command.add_argument("--task", required=True)
            command.add_argument("--max-cases", type=int, default=5)
        else:
            command.add_argument("--at", required=True, help="ISO timestamp with timezone")
        if name == "decision":
            command.add_argument("--action", required=True,
                                 choices=("accept", "decline", "remind-week", "never", "reminder-shown"))
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8-sig")
        document = json.loads(raw)
        if args.command == "prepare":
            result = prepare(document, args.task, args.max_cases)
        elif args.command == "offer":
            result = offer(document, args.at)
        else:
            result = decide(document, args.action, args.at)
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
