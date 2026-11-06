#!/usr/bin/env python3
"""Validate assessed review candidates and cap their display without dropping risks."""

from __future__ import annotations

import argparse
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


def prepare_report(
    document: dict, *, depth: str = "standard", max_findings: int | None = None,
) -> dict:
    require(depth in ("quick", "standard", "deep"), "invalid review depth")
    require(
        max_findings is None or (type(max_findings) is int and max_findings >= 0),
        "max_findings must be a nonnegative integer",
    )
    require(isinstance(document, dict), "input must be an object")
    references = document.get("references_read", [])
    require(
        isinstance(references, list) and all(nonempty(path) for path in references),
        "references_read must be an array of nonempty skill-relative paths",
    )
    require(
        depth == "quick" or FINDER_REFERENCE in references,
        f"{depth} review is INCOMPLETE: coordinator must read {FINDER_REFERENCE}",
    )
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
    displayed = retained if max_findings is None else retained[:max_findings]
    omitted = retained[len(displayed):]
    return {
        "verification_mode": mode, "depth": depth,
        "references_read": list(references),
        "findings": displayed, "retained_count": len(retained),
        "cut_count": len(omitted), "omitted_ids": [item["id"] for item in omitted],
        "has_blocker": any(item["priority"] in ("P0", "P1") for item in retained),
        "refuted": refuted, "rejected": rejected,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="JSON input file, or - for stdin")
    parser.add_argument("--depth", choices=("quick", "standard", "deep"), default="standard")
    parser.add_argument("--max-findings", type=int)
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        report = prepare_report(json.loads(raw), depth=args.depth, max_findings=args.max_findings)
    except (OSError, ValueError) as exc:
        print(f"Invalid review report: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
