#!/usr/bin/env python3
"""Validate assessed review candidates and cap their display without dropping risks."""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import re
import sys


PRIORITIES = ("P0", "P1", "P2", "P3")
CATEGORY_TIERS = {
    "correctness": 0, "security": 0, "reliability": 0,
    "ui": 0, "ux": 0, "accessibility": 0,
    "performance": 1, "coverage": 1,
    "cleanup": 2, "conventions": 2,
}
VERDICTS = ("CONFIRMED", "PLAUSIBLE", "REFUTED")
FINDER_REFERENCE = "references/finder-and-verifier.md"
SMALL_DELTA_REFERENCE = "references/delta-small.md"
DEPTHS = ("quick", "standard", "deep", "delta-small")
REFUTATIONS = (
    "contradicting-code", "invariant-or-type", "guard-in-diff",
    "no-observable-effect",
)


class ContractError(ValueError):
    """An assessment lacks the evidence needed by the review contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def citation_valid(value: object, *, needs_line: bool = True) -> bool:
    return (
        isinstance(value, dict)
        and nonempty(value.get("file"))
        and nonempty(value.get("quote"))
        and (
            not needs_line
            or (type(value.get("line")) is int and value["line"] > 0)
        )
    )


def check_coverage(document, references, retained):
    expected = set()
    for source in references:
        if isinstance(source, str):
            continue
        if "unresolved" in source:
            require(nonempty(source.get("path")) and nonempty(source["unresolved"]),
                    "identify the unresolved source and reason")
            require(not source.get("rule_ids"), "unresolved rule text cannot supply applicable IDs")
            continue
        for field in ("path", "source", "revision"):
            require(nonempty(source.get(field)), f"rule source needs {field}")
        ids = source.get("rule_ids")
        require(isinstance(ids, list) and all(nonempty(i) for i in ids), "declare applicable rule_ids")
        keys = {(source["path"], rule) for rule in ids}
        require(len(keys) == len(ids) and not keys & expected, "duplicate applicable rule")
        expected.update(keys)
    rows = document.get("convention_coverage")
    require(isinstance(rows, list), "declare convention_coverage, even when empty")
    seen = set()
    linked = set()
    valid_ids = {c["id"] for c in retained}
    for row in rows:
        require(isinstance(row, dict), "invalid convention coverage row")
        require(nonempty(row.get("path")) and nonempty(row.get("id")), "invalid coverage rule")
        key = (row["path"], row["id"])
        require(key in expected and key not in seen, f"unexpected coverage rule: {key}")
        seen.add(key)
        status = row.get("status")
        require(status in ("applied (findings)", "applied (none)", "not checked"), f"invalid status: {key}")
        if status == "applied (findings)":
            ids = row.get("findings")
            require(isinstance(ids, list) and ids and all(nonempty(i) and i in valid_ids for i in ids),
                    f"link {key} to retained findings before the display cap")
            linked.update(ids)
        if status == "not checked":
            require(nonempty(row.get("reason")), f"missing coverage reason: {key}")
    require(seen == expected, f"missing coverage for {sorted(expected - seen)}")
    missing = {c["id"] for c in retained if c["category"] == "conventions"} - linked
    require(not missing, f"convention findings missing from source coverage: {sorted(missing)}")
    return rows


def contract_questions(fields, retained):
    require(isinstance(fields, list), "contract_fields must be an array")
    questions = []
    valid_ids = {c["id"] for c in retained}
    for field in fields:
        require(isinstance(field, dict) and nonempty(field.get("field")), "name the wire field")
        require(nonempty(field.get("consumer_evidence")), "record consumer search or unavailable source")
        status = field.get("consumer")
        require(status in ("used", "unused", "unknown"), "declare consumer status")
        fact = field.get("external_fact")
        require(fact in ("confirmed", "assumed", "none"), "declare external fact status")
        if fact == "confirmed":
            require(nonempty(field.get("fact_evidence")), "cite the capture or vendor document")
        finding = field.get("finding")
        if finding is not None:
            require(nonempty(finding) and finding in valid_ids, "wire finding must name a retained CR ID")
        if fact == "assumed" or status == "unknown" or (status == "unused" and finding is None):
            require(nonempty(field.get("question")), "unresolved wire field needs a question to the author")
            questions.append({"field": field["field"], "question": field["question"]})
    return questions


def prepare_report(
    document: dict, *, depth: str = "standard", max_findings: int | None = None,
) -> dict:
    require(depth in DEPTHS, "invalid review depth")
    require(
        max_findings is None or (type(max_findings) is int and max_findings >= 0),
        "max_findings must be a nonnegative integer",
    )
    require(isinstance(document, dict), "input must be an object")
    references = document.get("references_read", [])
    require(
        isinstance(references, list) and all(nonempty(r) or isinstance(r, dict) for r in references),
        "references_read must contain reference paths or rule source records",
    )
    if depth != "quick":
        required_reference = SMALL_DELTA_REFERENCE if depth == "delta-small" else FINDER_REFERENCE
        require(required_reference in references,
                f"{depth} review is INCOMPLETE: coordinator must read {required_reference}")
    if depth == "delta-small":
        delta = document.get("delta")
        require(isinstance(delta, dict), "declare delta scope and required check results")
        for field in ("base", "head", "closures", "accessibility", "permissions", "mutants"):
            require(nonempty(delta.get(field)), f"delta: missing {field}")
        require(delta["base"] != delta["head"], "pin both revisions of the fix round")
        size = delta.get("logic_lines")
        require(type(size) is int and 0 <= size <= 60, "delta-small requires 0 to 60 changed logic lines")
    mode = document.get("verification_mode")
    require(mode in ("independent", "inline"), "declare verification_mode")
    candidates = document.get("candidates")
    require(isinstance(candidates, list), "candidates must be an array")
    retained, refuted, rejected = [], [], []
    identifiers: set[str] = set()
    for original in candidates:
        require(isinstance(original, dict), "candidate must be an object")
        candidate = deepcopy(original)
        identity = candidate.get("id")
        require(
            isinstance(identity, str) and re.fullmatch(r"CR-\d{3,}", identity) is not None
            and int(identity[3:]) > 0,
            "candidate must have a positive CR ID, such as CR-001",
        )
        require(identity not in identifiers, f"duplicate candidate ID: {identity}")
        identifiers.add(identity)
        for field in ("finder", "file", "summary", "failure_scenario"):
            require(nonempty(candidate.get(field)), f"{identity}: missing {field}")
        require(
            type(candidate.get("line")) is int and candidate["line"] > 0,
            f"{identity}: line must be a positive integer",
        )
        priority = candidate.get("priority")
        category = candidate.get("category")
        require(priority in PRIORITIES, f"{identity}: invalid priority")
        require(
            isinstance(category, str) and category in CATEGORY_TIERS,
            f"{identity}: invalid category",
        )
        if category == "conventions" and not citation_valid(
            candidate.get("rule"), needs_line=False,
        ):
            rejected.append({"id": identity, "reason": "missing quoted repository rule and path"})
            continue

        assessments = candidate.get("assessments")
        require(isinstance(assessments, list) and bool(assessments), f"{identity}: no assessment")
        require(depth == "deep" or len(assessments) == 1, f"{identity}: use one verifier outside deep mode")
        reviewers: set[str] = set()
        for assessment in assessments:
            require(isinstance(assessment, dict), f"{identity}: assessment must be an object")
            reviewer = assessment.get("reviewer")
            require(nonempty(reviewer), f"{identity}: missing reviewer")
            require(reviewer not in reviewers, f"{identity}: duplicate reviewer vote")
            reviewers.add(reviewer)
            require(
                mode == "inline" or reviewer != candidate["finder"],
                f"{identity}: independent verifier cannot be the finder",
            )
            verdict = assessment.get("verdict")
            require(verdict in VERDICTS, f"{identity}: invalid verification verdict")
            require(citation_valid(assessment.get("evidence")), f"{identity}: missing quoted file/line evidence")
            if verdict == "PLAUSIBLE":
                require(nonempty(assessment.get("confirmation")), f"{identity}: PLAUSIBLE needs a confirmation step")
            if verdict == "REFUTED":
                require(assessment.get("refutation") in REFUTATIONS, f"{identity}: invalid refutation basis")
                require(nonempty(assessment.get("reason")), f"{identity}: REFUTED needs a source-grounded reason")

        votes = {item["verdict"] for item in assessments}
        if votes == {"REFUTED"}:
            candidate["verdict"] = "REFUTED"
            refuted.append(candidate)
            continue
        disagreement = "REFUTED" in votes
        candidate["verdict"] = (
            "CONFIRMED" if "CONFIRMED" in votes and not disagreement else "PLAUSIBLE"
        )
        if disagreement:
            candidate["confirmation"] = (
                "Resolve the conflicting cited evidence against this failure scenario; "
                "run a narrow trigger check if the source trace remains inconclusive."
            )
        elif candidate["verdict"] == "PLAUSIBLE":
            candidate["confirmation"] = " ".join(
                item["confirmation"] for item in assessments if item["verdict"] == "PLAUSIBLE"
            )
        retained.append(candidate)

    retained.sort(key=lambda item: (
        PRIORITIES.index(item["priority"]), CATEGORY_TIERS[item["category"]], int(item["id"][3:]),
    ))
    coverage = check_coverage(document, references, retained)
    fields = document.get("contract_fields", [])
    questions = contract_questions(fields, retained)
    eligible = retained
    if depth == "delta-small":
        eligible = []
        extras = 0
        for item in retained:
            lane = item.get("delta_check")
            require(lane in ("closure", "accessibility", "permissions", "mutant", "extra"),
                    f"{item['id']}: declare delta_check")
            if lane == "extra":
                require(item["priority"] == "P3",
                        f"{item['id']}: use the ordinary delta for a material incidental finding")
                extras += 1
                if extras > 3:
                    continue
            eligible.append(item)
    # Reserve the best-ranked representative of each category, then fill spare slots.
    representatives = {}
    for item in eligible:
        representatives.setdefault(item["category"], item["id"])
    first = list(representatives.values())
    reserved = set(first)
    selection = first + [item["id"] for item in eligible if item["id"] not in reserved]
    chosen = set(selection[:max_findings])
    displayed = [item for item in retained if item["id"] in chosen]
    omitted = [item for item in retained if item["id"] not in chosen]
    return {
        "verification_mode": mode, "depth": depth,
        **({"delta": delta} if depth == "delta-small" else {}),
        "references_read": list(references),
        "rule_source_limits": [r for r in references if isinstance(r, dict) and (r.get("unresolved") or r.get("warning"))],
        "convention_coverage": coverage, "contract_fields": fields, "questions": questions,
        "further_findings_by_category": dict(Counter(item["category"] for item in omitted)),
        "findings": displayed, "retained_count": len(retained),
        "cut_count": len(omitted), "omitted_ids": [item["id"] for item in omitted],
        "has_blocker": any(item["priority"] in ("P0", "P1") for item in retained),
        "refuted": refuted, "rejected": rejected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSON input file, or - for stdin")
    parser.add_argument("--depth", choices=DEPTHS, default="standard")
    parser.add_argument("--max-findings", type=int)
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        report = prepare_report(json.loads(raw), depth=args.depth, max_findings=args.max_findings)
    except (OSError, ValueError) as exc:
        print(f"Invalid review report: {exc}", file=sys.stderr)
        return 2
    # Keep quoted rule text round-trippable on redirected legacy Windows consoles.
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
