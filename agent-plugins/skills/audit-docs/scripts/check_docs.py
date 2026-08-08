#!/usr/bin/env python3
"""Read-only, deterministic checks for repository Markdown documentation."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator
from urllib.parse import unquote


MARKDOWN_SUFFIXES = {".md", ".markdown"}
PATH_SUFFIXES = (
    "md|markdown|rst|adoc|html?|css|pdf|docx?|pptx?|xlsx?|csv|tsv|"
    "png|jpe?g|gif|svg|webp|ya?ml|json|toml|ini|txt|"
    "py|js|mjs|cjs|ts|tsx|jsx|go|rs|java|kt|kts|rb|php|cs|cpp|c|h|sh|ps1"
)
IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    "coverage",
    "__pycache__",
}
HISTORICAL_MARKERS = re.compile(
    r"\b(historical|history only|legacy example|external provenance|upstream provenance|"
    r"ported from|formerly located|old location|archived at)\b",
    re.IGNORECASE,
)
INLINE_LINK_RE = re.compile(
    r"!?\[[^\]]*\]\(\s*(?:<(?P<angle>[^>]+)>|(?P<plain>[^)\s]+))"
    r"(?:\s+[\"'][^)]*[\"'])?\s*\)"
)
REFERENCE_LINK_RE = re.compile(
    r"^\s*\[[^\]]+\]:\s*(?:<(?P<angle>[^>]+)>|(?P<plain>\S+))"
)
PLAIN_PATH_RE = re.compile(
    rf"(?<![\w:/\\])(?P<path>(?:\.{{1,2}}[\\/])?"
    rf"(?:[A-Za-z0-9_.-]+[\\/])+[A-Za-z0-9_.-]+\.(?:{PATH_SUFFIXES}))"
    r"(?::(?P<line>\d+))?(?![\w])",
    re.IGNORECASE,
)
INLINE_CODE_RE = re.compile(r"(`+)(.*?)(\1)")
ABSOLUTE_WINDOWS_RE = re.compile(r"^[A-Za-z]:[\\/]")
URL_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "ftp://")
SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    line: int
    message: str
    target: str | None = None


@dataclass(frozen=True)
class LinkRef:
    target: str
    line: int


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Markdown links, conservative plain paths, indexes, and explicit Unicode policies without writing files."
    )
    parser.add_argument("paths", nargs="*", help="Markdown files or directories to scan")
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository boundary used to resolve repo-relative plain paths (default: nearest .git parent or cwd)",
    )
    parser.add_argument(
        "--index",
        action="append",
        default=[],
        type=Path,
        help="Declared Markdown index to compare with its index root; repeat as needed",
    )
    parser.add_argument(
        "--index-root",
        type=Path,
        help="Directory whose Markdown files must appear in each --index (default: each index parent)",
    )
    parser.add_argument(
        "--prohibited-regex",
        action="append",
        default=[],
        help="Explicit repository-policy regex to flag in prose; repeat as needed",
    )
    parser.add_argument(
        "--prohibited-range",
        action="append",
        default=[],
        metavar="START-END",
        help="Explicit Unicode code-point range, for example 0400-04FF or U+0400-U+04FF",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--fail-on",
        choices=("critical", "warning", "never"),
        default="critical",
        help="Exit nonzero at this severity (default: critical)",
    )
    return parser.parse_args(argv)


def discover_repo_root(explicit: Path | None) -> Path:
    if explicit:
        return explicit.resolve()
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return str(path)


def iter_markdown(path: Path) -> Iterator[Path]:
    if path.is_symlink():
        return
    if path.is_file():
        if path.suffix.lower() in MARKDOWN_SUFFIXES:
            yield path
        return
    if not path.is_dir():
        return
    for current, dirnames, filenames in os.walk(path, followlinks=False):
        dirnames[:] = sorted(
            name
            for name in dirnames
            if name not in IGNORED_DIRS and not (Path(current) / name).is_symlink()
        )
        for filename in sorted(filenames):
            candidate = Path(current) / filename
            if not candidate.is_symlink() and candidate.suffix.lower() in MARKDOWN_SUFFIXES:
                yield candidate.resolve()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig", errors="replace").splitlines()


def replace_span(text: str, start: int, end: int) -> str:
    return text[:start] + (" " * (end - start)) + text[end:]


def strip_inline_code(text: str) -> str:
    result = text
    while True:
        match = INLINE_CODE_RE.search(result)
        if not match:
            return result
        result = replace_span(result, match.start(), match.end())


def prose_lines(path: Path) -> Iterator[tuple[int, str]]:
    fence_char: str | None = None
    fence_length = 0
    for number, original in enumerate(read_lines(path), start=1):
        stripped = original.lstrip()
        fence = re.match(r"(`{3,}|~{3,})", stripped)
        if fence:
            marker = fence.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_length = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_length:
                fence_char = None
                fence_length = 0
            continue
        if fence_char is None and not original.startswith(("    ", "\t")):
            yield number, strip_inline_code(original)


def extract_links(path: Path) -> list[LinkRef]:
    links: list[LinkRef] = []
    for line_number, prose in prose_lines(path):
        for match in INLINE_LINK_RE.finditer(prose):
            links.append(LinkRef(match.group("angle") or match.group("plain"), line_number))
        match = REFERENCE_LINK_RE.match(prose)
        if match:
            links.append(LinkRef(match.group("angle") or match.group("plain"), line_number))
    return links


def is_placeholder(target: str) -> bool:
    return any(token in target for token in ("<", ">", "{", "}", "$", "*", "%"))


def split_target(target: str) -> tuple[str, str]:
    target = target.strip()
    before_fragment, separator, fragment = target.partition("#")
    path_part = before_fragment.split("?", 1)[0]
    return unquote(path_part), unquote(fragment) if separator else ""


def is_external_or_absolute(path_part: str) -> bool:
    lowered = path_part.lower()
    return (
        lowered.startswith(URL_SCHEMES)
        or path_part.startswith(("/", "\\\\", "~"))
        or ABSOLUTE_WINDOWS_RE.match(path_part) is not None
    )


def resolve_markdown_target(source: Path, path_part: str) -> Path:
    normalized = path_part.replace("/", os.sep).replace("\\", os.sep)
    return (source.parent / normalized).resolve()


def github_anchors(path: Path) -> tuple[set[str], int]:
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    lines = read_lines(path)
    for _, prose in prose_lines(path):
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", prose)
        if heading:
            text = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", heading.group(1))
            text = re.sub(r"<[^>]+>", "", text)
            text = "".join(ch for ch in text.lower() if ch.isalnum() or ch in " _-")
            base = re.sub(r"[\s-]+", "-", text.strip())
            if base:
                count = seen.get(base, 0)
                anchors.add(base if count == 0 else f"{base}-{count}")
                seen[base] = count + 1
        for explicit in re.finditer(r"\bid=[\"']([^\"']+)[\"']", prose, re.IGNORECASE):
            anchors.add(explicit.group(1))
    return anchors, len(lines)


def check_anchor(
    source: Path,
    target: Path,
    fragment: str,
    line_number: int,
    repo_root: Path,
    anchor_cache: dict[Path, tuple[set[str], int]],
) -> Finding | None:
    if not fragment or not target.is_file() or target.suffix.lower() not in MARKDOWN_SUFFIXES:
        return None
    anchors, line_count = anchor_cache.setdefault(target, github_anchors(target))
    line_anchor = re.fullmatch(r"L(\d+)(?:-L(\d+))?", fragment, re.IGNORECASE)
    if line_anchor:
        end = int(line_anchor.group(2) or line_anchor.group(1))
        if end <= line_count:
            return None
    elif fragment in anchors or fragment.lower() in {anchor.lower() for anchor in anchors}:
        return None
    return Finding(
        "warning",
        "BROKEN_ANCHOR",
        display_path(source, repo_root),
        line_number,
        "Local Markdown anchor was not found; verify custom renderer behavior before reporting.",
        fragment,
    )


def check_links(
    path: Path,
    repo_root: Path,
    anchor_cache: dict[Path, tuple[set[str], int]],
) -> list[Finding]:
    findings: list[Finding] = []
    for link in extract_links(path):
        path_part, fragment = split_target(link.target)
        if is_placeholder(link.target) or (path_part and is_external_or_absolute(path_part)):
            continue
        target = path if not path_part else resolve_markdown_target(path, path_part)
        if not within(target, repo_root):
            findings.append(
                Finding(
                    "info",
                    "OUTSIDE_REPOSITORY",
                    display_path(path, repo_root),
                    link.line,
                    "Relative link resolves outside the repository and was not followed.",
                    link.target,
                )
            )
            continue
        if not target.exists():
            findings.append(
                Finding(
                    "critical",
                    "BROKEN_LINK",
                    display_path(path, repo_root),
                    link.line,
                    "Required local Markdown target does not exist.",
                    link.target,
                )
            )
            continue
        anchor_finding = check_anchor(path, target, fragment, link.line, repo_root, anchor_cache)
        if anchor_finding:
            findings.append(anchor_finding)
    return findings


def plain_path_candidates(source: Path, raw_path: str, repo_root: Path) -> list[Path]:
    normalized = raw_path.replace("/", os.sep).replace("\\", os.sep)
    if normalized.startswith((f".{os.sep}", f"..{os.sep}")):
        return [(source.parent / normalized).resolve()]
    candidates = [(repo_root / normalized).resolve(), (source.parent / normalized).resolve()]
    return list(dict.fromkeys(candidates))


def check_plain_paths(path: Path, repo_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, prose in prose_lines(path):
        if HISTORICAL_MARKERS.search(prose):
            continue
        if REFERENCE_LINK_RE.match(prose):
            continue
        without_links = prose
        spans = [match.span() for match in INLINE_LINK_RE.finditer(prose)]
        for start, end in reversed(spans):
            without_links = replace_span(without_links, start, end)
        for match in PLAIN_PATH_RE.finditer(without_links):
            raw_path = match.group("path")
            if is_placeholder(raw_path):
                continue
            parts = set(Path(raw_path.replace("\\", "/")).parts)
            if parts & IGNORED_DIRS:
                continue
            candidates = plain_path_candidates(path, raw_path, repo_root)
            existing = next((candidate for candidate in candidates if candidate.exists()), None)
            if existing is None:
                findings.append(
                    Finding(
                        "warning",
                        "MISSING_PLAIN_PATH",
                        display_path(path, repo_root),
                        line_number,
                        "Conservative plain repository path did not resolve; verify whether it is illustrative or historical.",
                        raw_path,
                    )
                )
                continue
            requested_line = match.group("line")
            if requested_line and existing.is_file():
                try:
                    line_count = len(read_lines(existing))
                except OSError:
                    continue
                if int(requested_line) > line_count:
                    findings.append(
                        Finding(
                            "warning",
                            "PLAIN_PATH_LINE_RANGE",
                            display_path(path, repo_root),
                            line_number,
                            "Plain path line reference exceeds the target file length.",
                            f"{raw_path}:{requested_line}",
                        )
                    )
    return findings


def parse_unicode_range(spec: str) -> tuple[int, int]:
    normalized = spec.upper().replace("U+", "")
    match = re.fullmatch(r"([0-9A-F]{1,6})-([0-9A-F]{1,6})", normalized)
    if not match:
        raise ValueError(f"invalid Unicode range {spec!r}; expected START-END, for example 0400-04FF")
    start, end = int(match.group(1), 16), int(match.group(2), 16)
    if start > end or end > 0x10FFFF:
        raise ValueError(f"invalid Unicode range {spec!r}")
    return start, end


def check_prohibited(
    path: Path,
    repo_root: Path,
    regexes: list[re.Pattern[str]],
    ranges: list[tuple[int, int, str]],
) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, prose in prose_lines(path):
        for pattern in regexes:
            match = pattern.search(prose)
            if match:
                findings.append(
                    Finding(
                        "warning",
                        "PROHIBITED_PATTERN",
                        display_path(path, repo_root),
                        line_number,
                        "Text matches an explicitly supplied repository-policy pattern.",
                        pattern.pattern,
                    )
                )
        for start, end, label in ranges:
            offending = next((char for char in prose if start <= ord(char) <= end), None)
            if offending:
                findings.append(
                    Finding(
                        "warning",
                        "PROHIBITED_UNICODE_RANGE",
                        display_path(path, repo_root),
                        line_number,
                        f"Text contains U+{ord(offending):04X} from an explicitly supplied prohibited range.",
                        label,
                    )
                )
    return findings


def resolve_cli_path(path: Path, repo_root: Path) -> Path:
    return path.resolve() if path.is_absolute() else (repo_root / path).resolve()


def check_indexes(
    indexes: list[Path], index_root: Path | None, repo_root: Path
) -> list[Finding]:
    findings: list[Finding] = []
    for raw_index in indexes:
        index = resolve_cli_path(raw_index, repo_root)
        if not index.is_file():
            findings.append(
                Finding("critical", "MISSING_INDEX", display_path(index, repo_root), 1, "Declared index file does not exist.")
            )
            continue
        root = resolve_cli_path(index_root, repo_root) if index_root else index.parent
        if not within(index, repo_root) or not within(root, repo_root):
            findings.append(
                Finding("critical", "INDEX_OUTSIDE_REPOSITORY", display_path(index, repo_root), 1, "Index or index root escapes the repository boundary.")
            )
            continue
        linked: set[Path] = set()
        for link in extract_links(index):
            path_part, _ = split_target(link.target)
            if not path_part or is_external_or_absolute(path_part) or is_placeholder(path_part):
                continue
            target = resolve_markdown_target(index, path_part)
            if target.suffix.lower() in MARKDOWN_SUFFIXES and target.exists() and within(target, root):
                linked.add(target)
        for candidate in iter_markdown(root):
            if candidate == index:
                continue
            if candidate not in linked:
                findings.append(
                    Finding(
                        "warning",
                        "INDEX_ORPHAN",
                        display_path(candidate, repo_root),
                        1,
                        f"Markdown file is not linked from declared index {display_path(index, repo_root)}.",
                    )
                )
    return findings


def sort_findings(findings: Iterable[Finding]) -> list[Finding]:
    return sorted(
        set(findings),
        key=lambda item: (SEVERITY_ORDER[item.severity], item.path.casefold(), item.line, item.code, item.target or ""),
    )


def print_results(findings: list[Finding], scanned: list[Path], repo_root: Path, output_format: str) -> None:
    counts = {severity: sum(item.severity == severity for item in findings) for severity in SEVERITY_ORDER}
    if output_format == "json":
        payload = {
            "repo_root": str(repo_root),
            "scanned_files": [display_path(path, repo_root) for path in scanned],
            "counts": counts,
            "findings": [asdict(item) for item in findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
        return
    print(
        f"Documentation check: {counts['critical']} critical, {counts['warning']} warning, "
        f"{counts['info']} info; scanned {len(scanned)} Markdown file(s)."
    )
    for item in findings:
        target = f" [{item.target}]" if item.target else ""
        print(f"{item.severity.upper()} {item.code} {item.path}:{item.line} {item.message}{target}")


def exit_code(findings: list[Finding], fail_on: str) -> int:
    if fail_on == "never":
        return 0
    threshold = SEVERITY_ORDER[fail_on]
    return 1 if any(SEVERITY_ORDER[item.severity] <= threshold for item in findings) else 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    repo_root = discover_repo_root(args.repo_root)
    raw_paths = [Path(value) for value in args.paths]
    if not raw_paths:
        raw_paths = [Path("docs") if (repo_root / "docs").is_dir() else Path(".")]

    findings: list[Finding] = []
    scanned_set: set[Path] = set()
    for raw_path in raw_paths:
        resolved = resolve_cli_path(raw_path, repo_root)
        if not within(resolved, repo_root):
            findings.append(
                Finding("critical", "SCOPE_OUTSIDE_REPOSITORY", str(resolved), 1, "Requested scope escapes the repository boundary.")
            )
            continue
        if not resolved.exists():
            findings.append(
                Finding("critical", "MISSING_SCOPE", display_path(resolved, repo_root), 1, "Requested documentation scope does not exist.")
            )
            continue
        scanned_set.update(iter_markdown(resolved))

    for raw_index in args.index:
        index = resolve_cli_path(raw_index, repo_root)
        if index.is_file() and within(index, repo_root):
            scanned_set.add(index)

    try:
        regexes = [re.compile(pattern) for pattern in args.prohibited_regex]
        ranges = [(*parse_unicode_range(spec), spec) for spec in args.prohibited_range]
    except (re.error, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    anchor_cache: dict[Path, tuple[set[str], int]] = {}
    scanned = sorted(scanned_set, key=lambda path: display_path(path, repo_root).casefold())
    for path in scanned:
        try:
            findings.extend(check_links(path, repo_root, anchor_cache))
            findings.extend(check_plain_paths(path, repo_root))
            findings.extend(check_prohibited(path, repo_root, regexes, ranges))
        except OSError as error:
            findings.append(
                Finding("critical", "READ_ERROR", display_path(path, repo_root), 1, f"Could not read Markdown file: {error}")
            )
    findings.extend(check_indexes(args.index, args.index_root, repo_root))
    ordered = sort_findings(findings)
    print_results(ordered, scanned, repo_root, args.format)
    return exit_code(ordered, args.fail_on)


if __name__ == "__main__":
    raise SystemExit(main())
