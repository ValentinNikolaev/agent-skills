"""Validate a private education project against the packaged v1 record vocabulary."""

from __future__ import annotations

import json
import math
import re
from graphlib import CycleError, TopologicalSorter
from pathlib import Path


class Invalid(ValueError):
    """A project or transition did not satisfy a declared contract."""


def require(ok, message):
    if not ok:
        raise Invalid(message)


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(Path(path).read_text(encoding="utf-8-sig"), object_pairs_hook=unique)


def resources():
    package = Path(__file__).resolve().parents[1]
    bundled = package / "references" / "education"
    return bundled if bundled.is_dir() else package.parents[1] / "shared" / "education"


def unique_index(records, label):
    require(isinstance(records, list), f"{label}: expected a list")
    indexed = {}
    for row in records:
        require(isinstance(row, dict), f"{label}: expected an object")
        key = row.get("id")
        require(isinstance(key, str) and re.fullmatch(r"[A-Za-z0-9_.-]+", key),
                f"{label}: invalid ID {key!r}")
        require(key not in indexed, f"{label}: duplicate ID {key}")
        indexed[key] = row
    return indexed


def acyclic(graph, label):
    try:
        return tuple(TopologicalSorter(graph).static_order())
    except CycleError as exc:
        raise Invalid(f"{label}: cycle {exc.args[-1]}") from exc


def check_fields(row, fields, check, at):
    require(isinstance(row, dict), f"{at}: expected object")
    for key, kind in fields.items():
        require(key in row, f"{at}: missing {key}")
        check(row[key], kind, f"{at}.{key}")


def positive_int(value):
    return type(value) is int and value > 0


def text_value(value):
    return isinstance(value, str) and bool(value.strip())


def check_bundle(bundle, alignment=False, reviewed=None):
    require(isinstance(bundle, dict) and type(bundle.get("schema_version")) is int
            and bundle["schema_version"] == 1, "unsupported project schema version")
    schema = load(resources() / "contracts.json")
    registry = load(resources() / "evidence.json")
    rules = unique_index(registry["rules"], "rules")
    sources = unique_index(bundle.get("sources", []), "project sources")
    for source in sources.values():
        require(all(text_value(source.get(k)) for k in ("title", "edition", "locator", "kind", "verification")),
                f"{source['id']}: missing provenance")
        if source["verification"] == "verified":
            require(text_value(source.get("checked")), f"{source['id']}: missing verification date")
    library_sources = unique_index(registry["sources"], "library sources")
    require(not sources.keys() & library_sources.keys(), "project source shadows library ID")
    artifacts = unique_index(bundle.get("artifacts"), "artifacts")
    pinned = {}
    reqs = {}
    for key, artifact in artifacts.items():
        require(positive_int(artifact.get("revision")), f"{key}: invalid revision")
        require(artifact.get("kind") in schema["artifacts"], f"{key}: unknown kind")
        pinned[f"{key}@{artifact['revision']}"] = artifact
        if artifact["kind"] == "CurriculumMap":
            data = artifact.get("data")
            require(isinstance(data, dict), f"{key}: missing data")
            for rid in unique_index(data.get("requirements"), key):
                require(rid not in reqs, f"duplicate requirement {rid}")
                reqs[rid] = key
    graph = {}
    owners = {o for spec in schema["artifacts"].values() for o in spec["owners"]} - {"*"}

    for key, artifact in artifacts.items():
        kind = artifact["kind"]
        spec = schema["artifacts"][kind]
        allowed = owners if "*" in spec["owners"] else spec["owners"]
        require(artifact.get("producer") in allowed, f"{key}: wrong producer")
        require(artifact.get("status") in ("draft", "accepted", "provisional"), f"{key}: invalid status")
        deps = artifact.get("depends_on")
        require(isinstance(deps, list) and all(text_value(d) and d in pinned for d in deps),
                f"{key}: missing or stale dependency")
        require(len(set(deps)) == len(deps), f"{key}: duplicate dependency")
        graph[key] = {pinned[d]["id"] for d in deps}

        def check(value, token, at):
            if token in ("texts",) or token.endswith(("+", "*")):
                required = token.endswith("+")
                item = "text" if token == "texts" else token[:-1]
                require(isinstance(value, list) and (value or not required), f"{at}: expected list {token}")
                for i, element in enumerate(value):
                    check(element, item, f"{at}[{i}]")
            elif token in schema["records"]:
                check_fields(value, schema["records"][token], check, at)
            elif token in schema["enums"]:
                require(value in schema["enums"][token], f"{at}: unknown {token}")
            elif token.startswith("@") or token == "ref":
                require(text_value(value) and value in deps, f"{at}: undeclared or stale reference")
                require(token == "ref" or pinned[value]["kind"] == token[1:], f"{at}: wrong target type")
            elif token in ("rule", "req", "source"):
                require(text_value(value), f"{at}: missing ID")
                if token == "req":
                    require(reqs.get(value) in graph[key], f"{at}: missing curriculum reference {value}")
                elif token == "source":
                    require(value in library_sources or value in sources, f"{at}: unknown source {value}")
                else:
                    require(value in rules, f"{at}: unknown rule {value}")
            elif token == "bool":
                require(type(value) is bool, f"{at}: expected boolean")
            elif token == "positive-int":
                require(positive_int(value), f"{at}: expected positive integer")
            elif token == "positive":
                require(type(value) in (float, int) and math.isfinite(value) and value > 0, f"{at}: invalid points")
            elif token == "count?":
                require(value is None or type(value) is int and value >= 0, f"{at}: invalid count")
            elif token in ("nullable", "text"):
                require(text_value(value) or token == "nullable" and value is None, f"{at}: expected {token}")
            else:
                raise Invalid(f"{at}: unknown field type {token}")

        data = artifact.get("data")
        check_fields(data, spec["fields"], check, key)
        check_semantics(kind, data, pinned, sources, key)

    acyclic(graph, "artifacts")
    if alignment:
        objectives = {ref for ref, a in pinned.items() if a["kind"] == "LearningObjective" and a["data"]["essential"]}
        require(objectives, "alignment: no essential objectives")
        accepted = [a for ref, a in pinned.items() if a["status"] != "draft"
                    and (reviewed is None or ref in reviewed)]
        taught = {o for a in accepted if a["kind"] == "LearningMaterial"
                 for s in a["data"]["sections"] for o in s["objectives"]}
        assessed = {o for a in accepted if a["kind"] == "AssessmentItem" for o in a["data"]["objectives"]}
        require(objectives <= taught and objectives <= assessed,
                f"alignment: missing teaching {sorted(objectives - taught)}, assessment {sorted(objectives - assessed)}")
    return pinned


def check_semantics(kind, data, pinned, sources, key):
    def official(source_id):
        entry = sources.get(source_id, {})
        return (entry.get("kind") == "official" and entry.get("verification") == "verified"
                and entry["locator"].startswith("https://"))

    if kind == "CurriculumMap":
        for req in data["requirements"]:
            if req["source"] is not None:
                require(req["source"] in sources, f"{key}: unknown curriculum source")
            if req["authority"] == "official":
                require(official(req["source"]) and req["anchor"], f"{key}: unverified official requirement")
    elif kind == "PrerequisiteGraph":
        concepts = data["concepts"]
        require(len(concepts) == len(set(concepts)), f"{key}: duplicate concept")
        graph = {c: set() for c in concepts}
        for edge in data["edges"]:
            a, b = edge["before"], edge["after"]
            require(a in graph and b in graph, f"{key}: missing prerequisite concept")
            if edge["relation"] == "strict":
                graph[b].add(a)
        acyclic(graph, key)
    elif kind == "LearningMaterial":
        unique_index(data["sections"], "sections")
    elif kind == "AssessmentItem":
        targets = pinned[data["blueprint"]]["data"]["targets"]
        require(set(data["objectives"]) <= set(targets), f"{key}: item outside blueprint")
    elif kind == "ExamPreparationPlan" and data["alignment"] == "official":
        require(data["edition"] and data["official_sources"] and all(official(s) for s in data["official_sources"]),
                f"{key}: official alignment requires verified edition and source")
    elif kind == "ReviewReport":
        for f in data["findings"]:
            require(f["target"] in data["targets"], f"{key}: finding outside review scope")
            require(f["status"] != "fixed" or f["retest"], f"{key}: fixed without retest")
            if f["severity"] in ("critical", "high") and f["status"] != "fixed":
                require(data["decision"] != "pass", f"{key}: unresolved blocking finding")
    elif kind == "AnalyticsReport":
        for m in data["measures"]:
            a, b = m["numerator"], m["denominator"]
            require(a is None or b is None or a <= b, f"{key}: numerator exceeds denominator")
