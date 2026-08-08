#!/usr/bin/env python3
"""Read-only validator for memory contract version 1."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple


CONTRACT_VERSION = "1"
ALLOWED_TYPES = {"project", "feedback", "reference"}
ALLOWED_PROVENANCE_KINDS = {
    "url",
    "file",
    "provider",
    "repository",
    "conversation",
    "other",
}
REFRESHABLE_KINDS = {"url", "file", "provider", "other"}
REQUIRED_FIELDS = {
    "memory_contract",
    "name",
    "description",
    "type",
    "related",
    "provenance",
    "last_updated",
    "last_reviewed",
}
ALLOWED_FIELDS = set(REQUIRED_FIELDS)
PROVENANCE_REQUIRED = {"kind", "locator", "retrieved_at"}
PROVENANCE_ALLOWED = PROVENANCE_REQUIRED | {"revision"}
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FILENAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*[.]md$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
TOP_KEY_RE = re.compile(r"^([a-z_][a-z0-9_]*):(?:[ ]*(.*))?$")
RELATED_ITEM_RE = re.compile(r"^  -[ ]+(.+?)\s*$")
PROVENANCE_FIRST_RE = re.compile(r"^  -[ ]+([a-z_][a-z0-9_]*):(?:[ ]*(.*))?$")
PROVENANCE_FIELD_RE = re.compile(r"^    ([a-z_][a-z0-9_]*):(?:[ ]*(.*))?$")
INDEX_RE = re.compile(
    r"^- \[([a-z0-9]+(?:-[a-z0-9]+)*[.]md)\]"
    r"\(([a-z0-9]+(?:-[a-z0-9]+)*[.]md)\)"
    r" — (project|feedback|reference) — (\S(?:.*\S)?)$"
)
LOCAL_LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+[.]md(?:#[^)]*)?)\)")
HEADING_RE = re.compile(r"^#{1,6}[ ]+")
CONFLICT_HEADING_RE = re.compile(
    r"^#{1,6}[ ]+(?:conflicts?|open questions?)[ ]*$", re.IGNORECASE
)
SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str
    line: Optional[int] = None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "line": self.line,
            "message": self.message,
            "path": self.path,
            "severity": self.severity,
        }


@dataclass
class Memory:
    path: Path
    text: str
    data: Dict[str, Any]
    body: str
    related: List[str]
    provenance: List[Dict[str, str]]
    parse_ok: bool


AddFinding = Callable[[str, str, str, str, Optional[int]], None]


def parse_cli(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate one memory root without modifying it."
    )
    parser.add_argument("memory_root", type=Path)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--today", help="Validation date in YYYY-MM-DD form")
    parser.add_argument("--stale-days", type=int, default=30)
    parser.add_argument("--source-stale-days", type=int, default=30)
    parser.add_argument("--file-limit", type=int, default=200)
    parser.add_argument("--index-line-limit", type=int, default=80)
    parser.add_argument("--warning-ratio", type=float, default=0.75)
    parser.add_argument("--critical-ratio", type=float, default=0.95)
    parser.add_argument("--enforce-limits", action="store_true")
    args = parser.parse_args(argv)

    if args.stale_days < 0 or args.source_stale_days < 0:
        parser.error("stale-day thresholds must be zero or greater")
    if args.file_limit <= 0 or args.index_line_limit <= 0:
        parser.error("capacity limits must be greater than zero")
    if not 0 < args.warning_ratio < args.critical_ratio <= 1:
        parser.error("ratios must satisfy 0 < warning < critical <= 1")
    return args


def parse_iso_date(value: str) -> Optional[date]:
    if not DATE_RE.fullmatch(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_scalar(
    raw: str,
    path: str,
    line: int,
    add: AddFinding,
) -> str:
    value = raw.strip()
    if not value:
        return ""
    if value.startswith('"') or value.endswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            add("critical", "FRONTMATTER_SYNTAX", path, "Invalid quoted scalar.", line)
            return value
        if not isinstance(parsed, str):
            add("critical", "FRONTMATTER_SYNTAX", path, "Scalar must be text.", line)
            return str(parsed)
        return parsed
    if value.startswith("'") or value.endswith("'"):
        if len(value) < 2 or not (value.startswith("'") and value.endswith("'")):
            add("critical", "FRONTMATTER_SYNTAX", path, "Invalid quoted scalar.", line)
            return value
        return value[1:-1].replace("''", "'")
    if value in {"|", ">"} or value.startswith("{") or value.startswith("["):
        add(
            "critical",
            "FRONTMATTER_SYNTAX",
            path,
            "Unsupported YAML construct in the portable schema.",
            line,
        )
    return value


def parse_frontmatter(
    path: Path,
    text: str,
    add: AddFinding,
) -> Memory:
    display = path.name
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        add(
            "critical",
            "FRONTMATTER_MISSING",
            display,
            "File must start with an exact --- frontmatter delimiter.",
            1,
        )
        return Memory(path, text, {}, text, [], [], False)

    close = next((i for i in range(1, len(lines)) if lines[i] == "---"), None)
    if close is None:
        add(
            "critical",
            "FRONTMATTER_UNCLOSED",
            display,
            "Frontmatter has no closing --- delimiter.",
            1,
        )
        return Memory(path, text, {}, "", [], [], False)

    data: Dict[str, Any] = {}
    related: List[str] = []
    provenance: List[Dict[str, str]] = []
    parse_ok = True
    i = 1

    while i < close:
        line_text = lines[i]
        line_no = i + 1
        if not line_text.strip() or line_text.lstrip().startswith("#"):
            i += 1
            continue
        if line_text.startswith((" ", "\t")):
            add(
                "critical",
                "FRONTMATTER_SYNTAX",
                display,
                "Unexpected indentation.",
                line_no,
            )
            parse_ok = False
            i += 1
            continue

        match = TOP_KEY_RE.fullmatch(line_text)
        if not match:
            add(
                "critical",
                "FRONTMATTER_SYNTAX",
                display,
                "Expected a top-level key and scalar value.",
                line_no,
            )
            parse_ok = False
            i += 1
            continue

        key, raw = match.group(1), match.group(2) or ""
        if key in data:
            add(
                "critical",
                "DUPLICATE_FIELD",
                display,
                "Duplicate frontmatter field: " + key,
                line_no,
            )
            parse_ok = False

        if key == "related":
            items: List[str] = []
            if raw.strip() == "[]":
                data[key] = items
                related = items
                i += 1
                continue
            if raw.strip():
                add(
                    "critical",
                    "FRONTMATTER_SYNTAX",
                    display,
                    "related must be [] or a two-space block list.",
                    line_no,
                )
                parse_ok = False
                data[key] = items
                related = items
                i += 1
                continue

            i += 1
            while i < close and (not lines[i].strip() or lines[i].startswith((" ", "\t"))):
                if not lines[i].strip():
                    i += 1
                    continue
                item_match = RELATED_ITEM_RE.fullmatch(lines[i])
                if not item_match:
                    add(
                        "critical",
                        "FRONTMATTER_SYNTAX",
                        display,
                        "related entries must use exactly two spaces and a dash.",
                        i + 1,
                    )
                    parse_ok = False
                else:
                    items.append(parse_scalar(item_match.group(1), display, i + 1, add))
                i += 1
            data[key] = items
            related = items
            continue

        if key == "provenance":
            entries: List[Dict[str, str]] = []
            if raw.strip() == "[]":
                data[key] = entries
                provenance = entries
                i += 1
                continue
            if raw.strip():
                add(
                    "critical",
                    "FRONTMATTER_SYNTAX",
                    display,
                    "provenance must be a block list of mappings.",
                    line_no,
                )
                parse_ok = False
                data[key] = entries
                provenance = entries
                i += 1
                continue

            current: Optional[Dict[str, str]] = None
            i += 1
            while i < close and (not lines[i].strip() or lines[i].startswith((" ", "\t"))):
                nested = lines[i]
                if not nested.strip():
                    i += 1
                    continue
                first_match = PROVENANCE_FIRST_RE.fullmatch(nested)
                field_match = PROVENANCE_FIELD_RE.fullmatch(nested)
                if first_match:
                    current = {"__line__": str(i + 1)}
                    entries.append(current)
                    field, field_raw = first_match.group(1), first_match.group(2) or ""
                elif field_match and current is not None:
                    field, field_raw = field_match.group(1), field_match.group(2) or ""
                else:
                    add(
                        "critical",
                        "FRONTMATTER_SYNTAX",
                        display,
                        "Invalid provenance indentation or mapping entry.",
                        i + 1,
                    )
                    parse_ok = False
                    i += 1
                    continue

                if field in current:
                    add(
                        "critical",
                        "DUPLICATE_PROVENANCE_FIELD",
                        display,
                        "Duplicate provenance field: " + field,
                        i + 1,
                    )
                    parse_ok = False
                current[field] = parse_scalar(field_raw, display, i + 1, add)
                i += 1
            data[key] = entries
            provenance = entries
            continue

        data[key] = parse_scalar(raw, display, line_no, add)
        i += 1

    body = "\n".join(lines[close + 1 :])
    return Memory(path, text, data, body, related, provenance, parse_ok)


def validate_memory_fields(
    memory: Memory,
    today: date,
    stale_days: int,
    source_stale_days: int,
    add: AddFinding,
) -> None:
    path = memory.path.name
    data = memory.data

    for field in sorted(REQUIRED_FIELDS - set(data)):
        add("critical", "MISSING_FIELD", path, "Missing required field: " + field, None)
    for field in sorted(set(data) - ALLOWED_FIELDS):
        add(
            "warning",
            "UNKNOWN_FIELD",
            path,
            "Field is outside memory contract version 1: " + field,
            None,
        )

    if data.get("memory_contract") != CONTRACT_VERSION:
        add(
            "warning",
            "CONTRACT_VERSION",
            path,
            "memory_contract must be 1.",
            None,
        )

    name = data.get("name", "")
    if not KEBAB_RE.fullmatch(name):
        add("warning", "INVALID_NAME", path, "name must be lowercase kebab-case.", None)
    if name and name != memory.path.stem:
        add(
            "warning",
            "NAME_FILENAME_MISMATCH",
            path,
            "name must equal the filename stem.",
            None,
        )

    description = data.get("description", "")
    if not description:
        add("warning", "EMPTY_DESCRIPTION", path, "description must be non-empty.", None)

    memory_type = data.get("type", "")
    if memory_type not in ALLOWED_TYPES:
        add(
            "warning",
            "INVALID_TYPE",
            path,
            "type must be project, feedback, or reference.",
            None,
        )

    if not isinstance(data.get("related"), list):
        add("critical", "INVALID_RELATED", path, "related must be a list.", None)

    seen_related = set()
    for target in memory.related:
        if target in seen_related:
            add(
                "warning",
                "DUPLICATE_RELATED",
                path,
                "Duplicate related entry: " + target,
                None,
            )
        seen_related.add(target)
        if not FILENAME_RE.fullmatch(target):
            add(
                "warning",
                "INVALID_RELATED",
                path,
                "related must contain local lowercase kebab-case basenames: " + target,
                None,
            )
        if target == path:
            add("warning", "SELF_RELATED", path, "A memory cannot relate to itself.", None)
        if target == "MEMORY.md":
            add("warning", "INVALID_RELATED", path, "MEMORY.md cannot be related.", None)

    if not memory.provenance:
        add(
            "critical",
            "MISSING_PROVENANCE",
            path,
            "provenance must contain at least one structured entry.",
            None,
        )

    seen_provenance = set()
    for entry in memory.provenance:
        entry_line = int(entry.get("__line__", "0")) or None
        keys = set(entry) - {"__line__"}
        for field in sorted(PROVENANCE_REQUIRED - keys):
            add(
                "critical",
                "MISSING_PROVENANCE_FIELD",
                path,
                "Provenance entry is missing: " + field,
                entry_line,
            )
        for field in sorted(keys - PROVENANCE_ALLOWED):
            add(
                "warning",
                "UNKNOWN_PROVENANCE_FIELD",
                path,
                "Provenance field is outside the contract: " + field,
                entry_line,
            )

        kind = entry.get("kind", "")
        locator = entry.get("locator", "")
        retrieved_raw = entry.get("retrieved_at", "")
        revision = entry.get("revision")

        if kind not in ALLOWED_PROVENANCE_KINDS:
            add(
                "warning",
                "INVALID_PROVENANCE_KIND",
                path,
                "Invalid provenance kind: " + kind,
                entry_line,
            )
        if not locator:
            add(
                "warning",
                "EMPTY_PROVENANCE_LOCATOR",
                path,
                "Provenance locator must be non-empty.",
                entry_line,
            )
        if kind == "url" and not locator.startswith(("https://", "http://")):
            add(
                "warning",
                "INVALID_URL_LOCATOR",
                path,
                "URL provenance locator must start with https:// or http://.",
                entry_line,
            )
        if revision is not None and not revision.strip():
            add(
                "warning",
                "EMPTY_PROVENANCE_REVISION",
                path,
                "revision must be omitted or non-empty.",
                entry_line,
            )

        retrieved = parse_iso_date(retrieved_raw)
        if retrieved is None:
            add(
                "warning",
                "INVALID_RETRIEVED_DATE",
                path,
                "retrieved_at must be a valid YYYY-MM-DD date.",
                entry_line,
            )
        elif retrieved > today:
            add(
                "warning",
                "FUTURE_RETRIEVED_DATE",
                path,
                "retrieved_at is later than the validation date.",
                entry_line,
            )
        elif kind in REFRESHABLE_KINDS and (today - retrieved).days > source_stale_days:
            add(
                "info",
                "SOURCE_REVIEW_DUE",
                path,
                "Refreshable provenance is older than "
                + str(source_stale_days)
                + " days.",
                entry_line,
            )

        identity = (kind, locator, revision or "")
        if identity in seen_provenance:
            add(
                "warning",
                "DUPLICATE_PROVENANCE",
                path,
                "Duplicate provenance identity.",
                entry_line,
            )
        seen_provenance.add(identity)

    parsed_dates: Dict[str, date] = {}
    for field in ("last_updated", "last_reviewed"):
        raw = data.get(field, "")
        parsed = parse_iso_date(raw)
        if parsed is None:
            if field in data:
                add(
                    "warning",
                    "INVALID_DATE",
                    path,
                    field + " must be a valid YYYY-MM-DD date.",
                    None,
                )
            continue
        parsed_dates[field] = parsed
        if parsed > today:
            add(
                "warning",
                "FUTURE_DATE",
                path,
                field + " is later than the validation date.",
                None,
            )

    updated = parsed_dates.get("last_updated")
    reviewed = parsed_dates.get("last_reviewed")
    if updated and reviewed and reviewed < updated:
        add(
            "warning",
            "REVIEW_BEFORE_UPDATE",
            path,
            "last_reviewed cannot be earlier than last_updated.",
            None,
        )
    if reviewed and reviewed <= today and (today - reviewed).days > stale_days:
        add(
            "info",
            "MEMORY_REVIEW_DUE",
            path,
            "last_reviewed is older than " + str(stale_days) + " days.",
            None,
        )

    markers = (
        re.search(r"^<<<<<<<", memory.body, re.MULTILINE),
        re.search(r"^=======$", memory.body, re.MULTILINE),
        re.search(r"^>>>>>>>", memory.body, re.MULTILINE),
    )
    body_line_start = (
        len(memory.text.splitlines()) - len(memory.body.splitlines()) + 1
    )
    if all(markers):
        add(
            "critical",
            "MERGE_CONFLICT",
            path,
            "Body contains unresolved source-control conflict markers.",
            body_line_start + memory.body[: markers[0].start()].count("\n"),
        )

    body_lines = memory.body.splitlines()
    for index, line_text in enumerate(body_lines):
        if not CONFLICT_HEADING_RE.fullmatch(line_text.strip()):
            continue
        has_content = False
        for following in body_lines[index + 1 :]:
            if HEADING_RE.match(following):
                break
            if following.strip():
                has_content = True
                break
        if has_content:
            add(
                "info",
                "DECLARED_CONFLICT",
                path,
                "Explicit conflict or open-question section requires review.",
                body_line_start + index,
            )


def validate_relationships(
    memories: Dict[str, Memory],
    add: AddFinding,
) -> None:
    for filename in sorted(memories, key=str.casefold):
        memory = memories[filename]
        for target in sorted(set(memory.related), key=str.casefold):
            if not FILENAME_RE.fullmatch(target) or target == filename:
                continue
            if target not in memories:
                add(
                    "critical",
                    "MISSING_RELATED",
                    filename,
                    "related target does not exist in this root: " + target,
                    None,
                )
                continue
            other = memories[target]
            if filename not in other.related:
                add(
                    "warning",
                    "NON_RECIPROCAL_RELATED",
                    filename,
                    target + " does not relate back to " + filename + ".",
                    None,
                )


def validate_duplicates(
    memories: Dict[str, Memory],
    add: AddFinding,
) -> None:
    seen_names: Dict[str, str] = {}
    seen_descriptions: Dict[str, str] = {}
    seen_bodies: Dict[str, str] = {}
    seen_case_names: Dict[str, str] = {}

    for filename in sorted(memories, key=str.casefold):
        memory = memories[filename]
        folded_filename = filename.casefold()
        if folded_filename in seen_case_names and seen_case_names[folded_filename] != filename:
            add(
                "warning",
                "CASE_COLLISION",
                filename,
                "Filename collides case-insensitively with "
                + seen_case_names[folded_filename]
                + ".",
                None,
            )
        else:
            seen_case_names[folded_filename] = filename

        name = str(memory.data.get("name", "")).strip().casefold()
        if name:
            if name in seen_names:
                add(
                    "warning",
                    "DUPLICATE_NAME",
                    filename,
                    "name duplicates " + seen_names[name] + ".",
                    None,
                )
            else:
                seen_names[name] = filename

        description = re.sub(
            r"\s+", " ", str(memory.data.get("description", "")).strip()
        ).casefold()
        if description:
            if description in seen_descriptions:
                add(
                    "warning",
                    "DUPLICATE_DESCRIPTION",
                    filename,
                    "description duplicates " + seen_descriptions[description] + ".",
                    None,
                )
            else:
                seen_descriptions[description] = filename

        body = re.sub(r"\s+", " ", memory.body.strip()).casefold()
        if len(body) >= 120:
            if body in seen_bodies:
                add(
                    "warning",
                    "DUPLICATE_BODY",
                    filename,
                    "Substantive body duplicates " + seen_bodies[body] + ".",
                    None,
                )
            else:
                seen_bodies[body] = filename


def validate_index(
    index_path: Optional[Path],
    index_text: Optional[str],
    memories: Dict[str, Memory],
    add: AddFinding,
) -> int:
    if index_path is None:
        add(
            "critical",
            "MISSING_INDEX",
            "MEMORY.md",
            "The selected root has no exact MEMORY.md index.",
            None,
        )
        return 0
    if index_text is None:
        return 0

    entries: Dict[str, Tuple[str, int]] = {}
    lines = index_text.splitlines()

    for line_no, line_text in enumerate(lines, 1):
        exact = INDEX_RE.fullmatch(line_text)
        local_links = [
            target
            for target in LOCAL_LINK_RE.findall(line_text)
            if not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)
            and not target.startswith(("/", "\\", "~"))
        ]
        if exact:
            label, target, entry_type, _purpose = exact.groups()
            if label != target:
                add(
                    "warning",
                    "INDEX_LABEL_TARGET",
                    "MEMORY.md",
                    "Link label and target must match.",
                    line_no,
                )
            if target in entries:
                add(
                    "warning",
                    "DUPLICATE_INDEX_ENTRY",
                    "MEMORY.md",
                    "Duplicate index entry: " + target,
                    line_no,
                )
            else:
                entries[target] = (entry_type, line_no)
            if target not in memories:
                add(
                    "critical",
                    "DEAD_INDEX_LINK",
                    "MEMORY.md",
                    "Index target does not exist: " + target,
                    line_no,
                )
            else:
                actual_type = memories[target].data.get("type")
                if actual_type and actual_type != entry_type:
                    add(
                        "warning",
                        "INDEX_TYPE_MISMATCH",
                        "MEMORY.md",
                        target + " type does not match its frontmatter.",
                        line_no,
                    )
            continue

        if local_links:
            add(
                "warning",
                "INDEX_GRAMMAR",
                "MEMORY.md",
                "Local Markdown links must use the exact index grammar.",
                line_no,
            )
            for raw_target in local_links:
                target = raw_target.split("#", 1)[0]
                if FILENAME_RE.fullmatch(target) and target not in memories:
                    add(
                        "critical",
                        "DEAD_INDEX_LINK",
                        "MEMORY.md",
                        "Local link target does not exist: " + target,
                        line_no,
                    )

    for filename in sorted(set(memories) - set(entries), key=str.casefold):
        add(
            "warning",
            "ORPHAN_MEMORY",
            filename,
            "Active memory is not listed in MEMORY.md.",
            None,
        )
    return sum(1 for line in lines if line.strip())


def add_capacity_findings(
    count: int,
    limit: int,
    metric: str,
    warning_ratio: float,
    critical_ratio: float,
    enforce: bool,
    add: AddFinding,
) -> None:
    ratio = count / limit
    if ratio < warning_ratio:
        return
    if ratio >= critical_ratio:
        severity = "critical" if enforce else "info"
        code = "CAPACITY_CRITICAL"
        threshold = critical_ratio
    else:
        severity = "warning" if enforce else "info"
        code = "CAPACITY_WARNING"
        threshold = warning_ratio
    mode = "enforced" if enforce else "advisory"
    add(
        severity,
        code,
        "MEMORY.md" if metric == "index lines" else ".",
        metric
        + " capacity is "
        + mode
        + ": "
        + str(count)
        + "/"
        + str(limit)
        + " (threshold "
        + format(threshold, ".2f")
        + ").",
        None,
    )


def inside_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
        return True
    except (OSError, ValueError):
        return False


def render(
    args: argparse.Namespace,
    root: Path,
    today: date,
    findings: List[Finding],
    file_count: int,
    index_lines: int,
) -> None:
    ordered = sorted(
        findings,
        key=lambda item: (
            SEVERITY_ORDER[item.severity],
            item.path.casefold(),
            item.line or 0,
            item.code,
            item.message,
        ),
    )
    counts = {
        severity: sum(item.severity == severity for item in ordered)
        for severity in ("critical", "warning", "info")
    }
    failed = counts["critical"] > 0 or counts["warning"] > 0
    payload = {
        "configuration": {
            "critical_ratio": args.critical_ratio,
            "enforce_limits": args.enforce_limits,
            "file_limit": args.file_limit,
            "index_line_limit": args.index_line_limit,
            "source_stale_days": args.source_stale_days,
            "stale_days": args.stale_days,
            "warning_ratio": args.warning_ratio,
        },
        "contract_version": int(CONTRACT_VERSION),
        "findings": [item.as_dict() for item in ordered],
        "root": str(root),
        "status": "fail" if failed else "pass",
        "summary": {
            "critical": counts["critical"],
            "files": file_count,
            "index_lines": index_lines,
            "info": counts["info"],
            "warning": counts["warning"],
        },
        "today": today.isoformat(),
    }

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return

    print("Memory Validation Report")
    print("========================")
    print("Root: " + str(root))
    print("Contract: " + CONTRACT_VERSION)
    print("Today: " + today.isoformat())
    print("Files: " + str(file_count) + "; index lines: " + str(index_lines))
    print(
        "Findings: "
        + str(counts["critical"])
        + " critical, "
        + str(counts["warning"])
        + " warning, "
        + str(counts["info"])
        + " info"
    )
    if ordered:
        print()
        for item in ordered:
            location = item.path
            if item.line is not None:
                location += ":" + str(item.line)
            print(
                "["
                + item.severity.upper()
                + "] "
                + item.code
                + " "
                + location
                + " - "
                + item.message
            )
    else:
        print("No findings.")
    print()
    print("Result: " + ("FAIL" if failed else "PASS"))


def emit_root_error(args: argparse.Namespace, message: str) -> None:
    if args.format == "json":
        print(
            json.dumps(
                {"error": message, "status": "invocation_error"},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print("validate_memory.py: error: " + message, file=sys.stderr)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_cli(argv)

    if args.today:
        today = parse_iso_date(args.today)
        if today is None:
            emit_root_error(args, "--today must be a valid YYYY-MM-DD date")
            return 2
    else:
        today = date.today()

    try:
        root = args.memory_root.resolve(strict=True)
    except OSError as exc:
        emit_root_error(args, "cannot resolve memory root: " + str(exc))
        return 2
    if not root.is_dir():
        emit_root_error(args, "memory root is not a directory: " + str(root))
        return 2

    findings: List[Finding] = []

    def add(
        severity: str,
        code: str,
        path: str,
        message: str,
        line: Optional[int] = None,
    ) -> None:
        findings.append(Finding(severity, code, path, message, line))

    candidates: List[Path] = []
    try:
        for item in root.iterdir():
            if item.name.casefold().endswith(".md") and (
                item.is_symlink() or item.is_file()
            ):
                candidates.append(item)
    except OSError as exc:
        emit_root_error(args, "cannot list memory root: " + str(exc))
        return 2
    candidates.sort(key=lambda item: (item.name.casefold(), item.name))

    index_path: Optional[Path] = None
    index_text: Optional[str] = None
    memories: Dict[str, Memory] = {}

    for path in candidates:
        if path.is_symlink() and not inside_root(path, root):
            add(
                "critical",
                "CROSS_ROOT_SYMLINK",
                path.name,
                "Validator will not follow a memory-file symlink outside the root.",
                None,
            )
            if path.name == "MEMORY.md":
                index_path = path
            continue

        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            add(
                "critical",
                "UNREADABLE_FILE",
                path.name,
                "Cannot read UTF-8 file: " + str(exc),
                None,
            )
            if path.name == "MEMORY.md":
                index_path = path
            continue

        if path.name == "MEMORY.md":
            index_path = path
            index_text = text
            continue

        if not FILENAME_RE.fullmatch(path.name):
            add(
                "warning",
                "INVALID_FILENAME",
                path.name,
                "Memory filename must be lowercase kebab-case with .md.",
                None,
            )
        memory = parse_frontmatter(path, text, add)
        memories[path.name] = memory
        validate_memory_fields(
            memory,
            today,
            args.stale_days,
            args.source_stale_days,
            add,
        )

    validate_relationships(memories, add)
    validate_duplicates(memories, add)
    index_lines = validate_index(index_path, index_text, memories, add)

    add_capacity_findings(
        len(memories),
        args.file_limit,
        "file count",
        args.warning_ratio,
        args.critical_ratio,
        args.enforce_limits,
        add,
    )
    add_capacity_findings(
        index_lines,
        args.index_line_limit,
        "index lines",
        args.warning_ratio,
        args.critical_ratio,
        args.enforce_limits,
        add,
    )

    render(args, root, today, findings, len(memories), index_lines)
    return 1 if any(item.severity in {"critical", "warning"} for item in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
