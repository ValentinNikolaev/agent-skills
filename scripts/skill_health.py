#!/usr/bin/env python3
"""Periodic healthcheck for the canonical skill packages.

A release-preparation step, not part of generation, validation, or CI.

    python scripts/skill_health.py due      # is a healthcheck due for the next release?
    python scripts/skill_health.py check    # compute metrics and compare with the baseline
    python scripts/skill_health.py record   # write the new baseline after findings are handled

``due`` and ``check`` never write. ``record`` writes only the ledger
(``docs/skill-health.json`` by default), which does not bump the plugin version.
Standard library only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import generate_skill_wrappers as wrappers  # noqa: E402
import validate_skills as validator  # noqa: E402

LEDGER_SCHEMA = 1
DEFAULT_LEDGER = Path("docs/skill-health.json")
CHECK_KINDS = ("full-audit", "delta-review")
SEVERITY_ORDER = {"error": 0, "warn": 1, "info": 2}
MAX_HISTORY = 20

DEFAULT_SETTINGS: dict[str, Any] = {
    # A healthcheck is due when the next release's major reaches the last
    # checked major plus this many majors. Minor releases do not count.
    "interval_majors": 3,
    # Hard ceiling for one SKILL.md body. Null uses the validator's constant.
    "body_word_ceiling": None,
    # Flag a body that grew by more than this many words since the baseline.
    "body_growth_words": 150,
    # A description longer than this is flagged; the total budget is separate.
    "description_max_chars": 250,
    # "As of <date>" facts older than this many days are flagged.
    "stale_fact_days": 180,
    # Sentences shorter than this (normalized) are not compared across skills.
    "shared_sentence_min_chars": 60,
    # Near-duplicate file pairs: shared fraction of the smaller file's 6-grams.
    "near_duplicate_containment": 0.5,
    "near_duplicate_min_shared": 40,
    # File names whose copies are intentionally identical across skills.
    "duplicate_allowlist_files": ["memory-contract.md"],
    # Skills that legitimately show repository commands such as python scripts/...
    "bare_script_allowlist_skills": ["wrap-agent-skill"],
    # Names that no longer exist and must not appear as backticked skill names.
    "retired_skill_names": [
        "stop-slop",
        "create-github-pages",
        "improve-github-pages",
        "audit-github-pages-ux",
        "github-pages-content-architecture",
        "github-pages-visual-system",
    ],
    # Keys in agents/openai.yaml shared by at most this fraction of skills are
    # reported as outliers.
    "yaml_outlier_fraction": 0.1,
}


class HealthError(RuntimeError):
    """A user-actionable failure."""


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------


def empty_ledger() -> dict[str, Any]:
    return {
        "schema": LEDGER_SCHEMA,
        "settings": dict(DEFAULT_SETTINGS),
        "last_check": None,
        "baseline": None,
        "open_items": [],
        "history": [],
    }


def load_ledger(path: Path) -> dict[str, Any]:
    """Load the ledger, or an empty one when none has been recorded yet."""
    ledger = empty_ledger()
    if not path.is_file():
        return ledger
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise HealthError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise HealthError(f"{path}: expected a JSON object")
    if data.get("schema", LEDGER_SCHEMA) != LEDGER_SCHEMA:
        raise HealthError(f"{path}: unsupported ledger schema {data.get('schema')!r}")
    settings = data.get("settings")
    if settings is not None and not isinstance(settings, dict):
        raise HealthError(f"{path}: settings must be an object")
    ledger.update({key: value for key, value in data.items() if key != "settings"})
    ledger["settings"] = {**DEFAULT_SETTINGS, **(settings or {})}
    interval = ledger["settings"]["interval_majors"]
    if not isinstance(interval, int) or isinstance(interval, bool) or interval < 1:
        raise HealthError(f"{path}: settings.interval_majors must be a positive integer")
    return ledger


def write_ledger(path: Path, ledger: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


# ---------------------------------------------------------------------------
# Versions and git
# ---------------------------------------------------------------------------

VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def version_tuple(version: str | None) -> tuple[int, int, int] | None:
    if not version:
        return None
    match = VERSION_RE.match(version)
    return tuple(int(part) for part in match.groups()) if match else None  # type: ignore[return-value]


def version_core(version: str | None) -> str | None:
    parts = version_tuple(version)
    return ".".join(str(part) for part in parts) if parts else None


def git(repo_root: Path, *args: str) -> str | None:
    """Run a read-only git command; return stdout, or None on any failure."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=False,
            capture_output=True,
            encoding="utf-8",
        )
    except OSError:
        return None
    return result.stdout if result.returncode == 0 else None


def manifest_version_from_text(text: str | None) -> str | None:
    if text is None:
        return None
    try:
        version = json.loads(text.lstrip("﻿")).get("version")
    except (json.JSONDecodeError, AttributeError):
        return None
    return version if isinstance(version, str) else None


def read_versions(repo_root: Path) -> dict[str, dict[str, str | None]]:
    """Return committed and working-tree manifest versions per platform."""
    versions: dict[str, dict[str, str | None]] = {}
    for platform in ("claude", "codex"):
        relative = f".{platform}-plugin/plugin.json"
        path = repo_root / relative
        working = None
        if path.is_file():
            working = manifest_version_from_text(path.read_text(encoding="utf-8-sig"))
        committed = manifest_version_from_text(git(repo_root, "show", f"HEAD:{relative}"))
        versions[platform] = {"committed": committed, "working": working}
    return versions


def combine(versions: dict[str, dict[str, str | None]], which: str) -> str | None:
    cores = {version_core(item[which]) for item in versions.values()} - {None}
    if not cores:
        return None
    if len(cores) > 1:
        raise HealthError(
            f"Claude and Codex {which} version cores differ: "
            + ", ".join(sorted(cores))
        )
    return cores.pop()


def decide_due(
    next_major: int | None, last_major: int | None, interval: int
) -> tuple[bool, str]:
    """Decide from the recorded major, never from a modulo of the version."""
    if last_major is None:
        return True, "no healthcheck baseline is recorded"
    if next_major is None:
        return False, "the next release version is unknown"
    threshold = last_major + interval
    if next_major >= threshold:
        return True, f"next major v{next_major} reaches v{last_major} + {interval} = v{threshold}"
    return False, f"next major v{next_major} is below v{last_major} + {interval} = v{threshold}"


def due_state(repo_root: Path, ledger: dict[str, Any], *, project: bool = True) -> dict[str, Any]:
    versions = read_versions(repo_root)
    committed = combine(versions, "committed")
    working = combine(versions, "working")
    prepared = None
    if working and committed and version_tuple(working) > version_tuple(committed):
        prepared = working

    projection: list[Any] = []
    projection_error = None
    if project:
        try:
            projection = wrappers.project_release(repo_root)
        except (wrappers.GenerationError, OSError) as exc:
            projection_error = str(exc)
    bumps = [item for item in projection if item.bump and item.projected]
    projected_bump = None
    projected_version = None
    if bumps:
        projected_version = max((item.projected for item in bumps), key=version_tuple)
        projected_bump = "major" if any(item.bump == "major" for item in bumps) else "minor"

    candidates = [item for item in (working, prepared, projected_version) if item]
    next_version = max(candidates, key=version_tuple) if candidates else None
    next_major = version_tuple(next_version)[0] if next_version else None

    last = ledger.get("last_check")
    last_major = None
    if isinstance(last, dict) and isinstance(last.get("major"), int):
        last_major = last["major"]
    interval = ledger["settings"]["interval_majors"]
    due, reason = decide_due(next_major, last_major, interval)
    return {
        "committed_version": committed,
        "working_tree_version": working,
        "prepared_version": prepared,
        "projected_bump": projected_bump,
        "projected_version": projected_version,
        "projection_error": projection_error,
        "next_release_version": next_version,
        "next_major": next_major,
        "last_check": last if isinstance(last, dict) else None,
        "last_check_major": last_major,
        "interval_majors": interval,
        "due": due,
        "reason": reason,
    }


def render_due(state: dict[str, Any]) -> str:
    last = state["last_check"]
    if last:
        last_text = (
            f"v{state['last_check_major']} ({last.get('kind', 'unknown')}, "
            f"{last.get('date', 'unknown date')}, commit {str(last.get('commit') or 'unknown')[:12]})"
        )
    else:
        last_text = "none recorded"
    projected = (
        f"{state['projected_bump']} -> {state['projected_version']}"
        if state["projected_bump"]
        else "no generation change"
    )
    if state["projection_error"]:
        projected = f"unavailable ({state['projection_error']})"
    lines = [
        f"Committed version:      {state['committed_version'] or 'unknown'}",
        f"Working-tree version:   {state['working_tree_version'] or 'unknown'}",
        f"Prepared version:       {state['prepared_version'] or 'none'}",
        f"Projected bump:         {projected}",
        f"Next release version:   {state['next_release_version'] or 'unknown'}",
        f"Last healthcheck:       {last_text}",
        f"Interval:               every {state['interval_majors']} major versions",
        f"Healthcheck:            {'DUE' if state['due'] else 'NOT DUE'} ({state['reason']})",
    ]
    if state["due"] and not last:
        lines.append(
            "Next step:              run `check`, handle the findings, then `record`."
        )
    elif state["due"]:
        lines.append(
            "Next step:              run `check`, review the delta, then `record`."
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

FENCE_RE = re.compile(r"```.*?```", re.S)
MD_LINK_RE = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
SENTENCE_SPLIT_RE = re.compile(
    r"(?<=[.!?;:])\s+|\n\s*\n|\n\s*[-*]\s+|\n\s*\d+\.\s+|\n#+\s+|\|"
)
BARE_PYTHON_RE = re.compile(r"(?<![\w/\"'<>.-])python3?\s+(?:-[A-Za-z]\s+)*(?:\./)?scripts/")
AS_OF_RE = re.compile(
    r"\b(?:[Aa]s of|[Vv]erified on|[Cc]hecked on)\s+"
    r"(\d{4}-\d{2}-\d{2}|[A-Z][a-z]+ \d{1,2},? \d{4}|[A-Z][a-z]+ \d{4})"
)
MILESTONE_PATTERNS = (
    re.compile(
        r"\b(?:removal|removed|retirement|retired|sunset|deprecation)\b[^.\n]{0,40}?"
        r"\b(?:in|for|at|by|before)\s+(?:the\s+)?v(\d+)\b",
        re.I,
    ),
    re.compile(r"\b(?:through|until)\s+v(\d+)\b", re.I),
    re.compile(r"\bremove(?:d)?\s+(?:it\s+)?in\s+(?:the\s+)?v(\d+)\b", re.I),
)
BACKTICK_NAME_RE = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`")
ROUTING_WORD_RE = re.compile(
    r"\b(?:route|routes|routed|routing|hand(?:s|ed)? off|defer|delegate|neighbou?rs?|"
    r"instead|belongs?|owns?|owned by|use|uses)\b",
    re.I,
)


def read_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :]
    return text


def markdown_files(skill: wrappers.SourceSkill) -> list[Path]:
    return sorted(path for path in skill.directory.rglob("*.md") if path.is_file())


def sentence_key(sentence: str) -> str:
    return hashlib.sha1(sentence.encode("utf-8")).hexdigest()[:12]


def normalized_sentences(text: str, minimum: int) -> dict[str, str]:
    """Return {normalized sentence: original-ish sentence} for long sentences."""
    text = FENCE_RE.sub(" ", text)
    found: dict[str, str] = {}
    for raw in SENTENCE_SPLIT_RE.split(text):
        collapsed = re.sub(r"\s+", " ", raw).strip(" -*#>`")
        normalized = re.sub(r"[`*_]", "", collapsed).lower()
        if len(normalized) >= minimum:
            found.setdefault(normalized, collapsed)
    return found


def shared_sentence_groups(
    skills: Sequence[wrappers.SourceSkill], settings: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    allow = set(settings["duplicate_allowlist_files"])
    minimum = settings["shared_sentence_min_chars"]
    where: dict[str, dict[str, Any]] = {}
    for skill in skills:
        for path in markdown_files(skill):
            if path.name in allow or path.name.startswith(("LICENSE", "NOTICE")):
                continue
            text = read_markdown(path)
            if path.name == "SKILL.md":
                text = strip_frontmatter(text)
            relative = path.relative_to(skill.directory).as_posix()
            for normalized, original in normalized_sentences(text, minimum).items():
                entry = where.setdefault(normalized, {"text": original, "skills": {}})
                entry["skills"].setdefault(skill.name, []).append(relative)
    return {
        sentence_key(normalized): {
            "text": entry["text"],
            "skills": {name: sorted(files) for name, files in sorted(entry["skills"].items())},
        }
        for normalized, entry in where.items()
        if len(entry["skills"]) > 1
    }


def reference_orphans(skill: wrappers.SourceSkill) -> list[str]:
    references = skill.directory / "references"
    if not references.is_dir():
        return []
    files = sorted(path for path in references.rglob("*") if path.is_file())
    sources = [skill.directory / "SKILL.md"] + [path for path in files if path.suffix == ".md"]
    linked: set[Path] = set()
    texts: list[str] = []
    for source in sources:
        text = read_markdown(source)
        texts.append(text)
        for target in MD_LINK_RE.findall(text):
            if "://" in target or target.startswith(("mailto:", "/")):
                continue
            linked.add((source.parent / target).resolve())
    joined = "\n".join(texts)
    orphans = []
    for path in files:
        relative = path.relative_to(skill.directory).as_posix()
        if path.resolve() in linked:
            continue
        if relative in joined:
            continue
        orphans.append(relative)
    return orphans


def bare_python_lines(skill: wrappers.SourceSkill) -> list[tuple[str, int]]:
    hits = []
    for path in markdown_files(skill):
        for number, line in enumerate(read_markdown(path).splitlines(), 1):
            if BARE_PYTHON_RE.search(line):
                hits.append((path.relative_to(skill.directory).as_posix(), number))
    return hits


def milestone_hits(skill: wrappers.SourceSkill) -> list[tuple[str, int, int, str]]:
    hits = []
    for path in markdown_files(skill):
        relative = path.relative_to(skill.directory).as_posix()
        for number, line in enumerate(read_markdown(path).splitlines(), 1):
            for pattern in MILESTONE_PATTERNS:
                for match in pattern.finditer(line):
                    hits.append((relative, number, int(match.group(1)), match.group(0)))
    return hits


def parse_fact_date(raw: str) -> date | None:
    raw = raw.replace(",", "")
    for fmt in ("%Y-%m-%d", "%B %d %Y", "%b %d %Y", "%B %Y", "%b %Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def stale_fact_hits(
    skill: wrappers.SourceSkill, today: date, max_days: int
) -> list[tuple[str, int, str, int]]:
    hits = []
    for path in markdown_files(skill):
        relative = path.relative_to(skill.directory).as_posix()
        for number, line in enumerate(read_markdown(path).splitlines(), 1):
            for match in AS_OF_RE.finditer(line):
                parsed = parse_fact_date(match.group(1))
                if parsed and (today - parsed).days > max_days:
                    hits.append((relative, number, match.group(0), (today - parsed).days))
    return hits


def stale_skill_names(
    skill: wrappers.SourceSkill,
    canonical: set[str],
    vocabulary: set[str],
    retired: set[str],
) -> list[tuple[int, str]]:
    hits = []
    text = strip_frontmatter(read_markdown(skill.skill_file))
    offset = len(read_markdown(skill.skill_file).splitlines()) - len(text.splitlines())
    for number, line in enumerate(text.splitlines(), 1 + offset):
        for token in BACKTICK_NAME_RE.findall(line):
            if token in canonical:
                continue
            words = token.split("-")
            looks_like_skill = all(word in vocabulary for word in words)
            if token in retired or (looks_like_skill and ROUTING_WORD_RE.search(line)):
                hits.append((number, token))
    return hits


def shingles(text: str, size: int = 6) -> set[str]:
    words = re.sub(r"[^a-zа-я0-9 ]+", " ", text.lower()).split()
    return {" ".join(words[i : i + size]) for i in range(len(words) - size + 1)}


def near_duplicate_pairs(
    skills: Sequence[wrappers.SourceSkill], settings: dict[str, Any]
) -> list[dict[str, Any]]:
    allow = set(settings["duplicate_allowlist_files"])
    documents: dict[str, tuple[str, set[str]]] = {}
    for skill in skills:
        for path in markdown_files(skill):
            if path.name in allow or path.name.startswith(("LICENSE", "NOTICE")):
                continue
            text = FENCE_RE.sub(" ", read_markdown(path))
            sh = shingles(text)
            if len(sh) > settings["near_duplicate_min_shared"]:
                key = f"{skill.name}/{path.relative_to(skill.directory).as_posix()}"
                documents[key] = (skill.name, sh)
    keys = sorted(documents)
    pairs = []
    for index, left in enumerate(keys):
        for right in keys[index + 1 :]:
            if documents[left][0] == documents[right][0]:
                continue
            shared = len(documents[left][1] & documents[right][1])
            if shared < settings["near_duplicate_min_shared"]:
                continue
            containment = shared / min(len(documents[left][1]), len(documents[right][1]))
            if containment >= settings["near_duplicate_containment"]:
                pairs.append(
                    {
                        "pair": f"{left} <-> {right}",
                        "containment": round(containment, 2),
                        "shared": shared,
                    }
                )
    return pairs


def read_yaml_keys(skill: wrappers.SourceSkill) -> tuple[set[str], dict[str, str]]:
    """Return top-level and dotted interface keys plus short_description."""
    path = skill.directory / "agents" / "openai.yaml"
    keys: set[str] = set()
    values: dict[str, str] = {}
    if not path.is_file():
        return keys, values
    section = None
    for line in read_markdown(path).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        top = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        nested = re.match(r"^  ([A-Za-z0-9_-]+):\s*(.*)$", line)
        if top:
            section = top.group(1)
            keys.add(section)
        elif nested and section:
            keys.add(f"{section}.{nested.group(1)}")
            if section == "interface" and nested.group(1) == "short_description":
                values["short_description"] = nested.group(2).strip().strip("\"'")
    return keys, values


def short_hash(text: str | None) -> str | None:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12] if text is not None else None


def compute_metrics(
    repo_root: Path, settings: dict[str, Any], today: date
) -> dict[str, Any]:
    """Compute every metric from the working tree without writing anything."""
    source_root = (repo_root / wrappers.DEFAULT_SOURCE_DIR).resolve()
    skills = wrappers.discover_skills(source_root, [])
    canonical = {skill.name for skill in skills}
    vocabulary = {word for name in canonical for word in name.split("-")}
    retired = set(settings["retired_skill_names"])
    summaries = {
        name: summary
        for _heading, group in wrappers.README_SKILL_GROUPS
        for name, summary in group.items()
    }

    per_skill: dict[str, dict[str, Any]] = {}
    yaml_keys: dict[str, set[str]] = {}
    for skill in skills:
        keys, values = read_yaml_keys(skill)
        yaml_keys[skill.name] = keys
        per_skill[skill.name] = {
            "body_words": len(skill.body.split()),
            "description_chars": len(skill.description or ""),
            "description_hash": short_hash(skill.description),
            "short_description_hash": short_hash(values.get("short_description")),
            "readme_summary_hash": short_hash(summaries.get(skill.name)),
        }

    routing_chars = sum(len(skill.name) + len(skill.description or "") for skill in skills)
    bare_allow = set(settings["bare_script_allowlist_skills"])
    metrics: dict[str, Any] = {
        "skill_count": len(skills),
        "skills": per_skill,
        "routing_chars": routing_chars,
        "routing_budget": validator.ROUTING_METADATA_BUDGET,
        "shared_sentences": shared_sentence_groups(skills, settings),
        "orphan_references": {
            skill.name: orphans for skill in skills if (orphans := reference_orphans(skill))
        },
        "bare_python": {
            skill.name: [f"{path}:{line}" for path, line in hits]
            for skill in skills
            if skill.name not in bare_allow and (hits := bare_python_lines(skill))
        },
        "milestones": {
            skill.name: [
                {"path": path, "line": line, "major": major, "text": text}
                for path, line, major, text in hits
            ]
            for skill in skills
            if (hits := milestone_hits(skill))
        },
        "stale_skill_names": {
            skill.name: [{"line": line, "name": name} for line, name in hits]
            for skill in skills
            if (hits := stale_skill_names(skill, canonical, vocabulary, retired))
        },
        "stale_facts": {
            skill.name: [
                {"path": path, "line": line, "text": text, "age_days": age}
                for path, line, text, age in hits
            ]
            for skill in skills
            if (hits := stale_fact_hits(skill, today, settings["stale_fact_days"]))
        },
        "near_duplicates": near_duplicate_pairs(skills, settings),
    }

    counts: dict[str, int] = {}
    for keys in yaml_keys.values():
        for key in keys:
            counts[key] = counts.get(key, 0) + 1
    limit = settings["yaml_outlier_fraction"] * max(len(skills), 1)
    outliers = {
        key: sorted(name for name, keys in yaml_keys.items() if key in keys)
        for key, count in sorted(counts.items())
        if count <= limit
    }
    # A nested key adds nothing when its parent section is already reported.
    metrics["yaml_outliers"] = {
        key: names
        for key, names in outliers.items()
        if "." not in key or outliers.get(key.split(".", 1)[0]) != names
    }
    return metrics


def baseline_from_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "skills": {
            name: dict(values) for name, values in sorted(metrics["skills"].items())
        },
        "routing_chars": metrics["routing_chars"],
        "shared_sentence_keys": sorted(metrics["shared_sentences"]),
        "near_duplicate_pairs": sorted(item["pair"] for item in metrics["near_duplicates"]),
    }


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------


def finding(
    metric: str,
    severity: str,
    message: str,
    *,
    skill: str | None = None,
    location: str | None = None,
) -> dict[str, Any]:
    return {
        "metric": metric,
        "severity": severity,
        "skill": skill,
        "location": location,
        "message": message,
    }


def evaluate(
    metrics: dict[str, Any],
    settings: dict[str, Any],
    baseline: dict[str, Any] | None,
    next_major: int | None,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    ceiling = settings["body_word_ceiling"] or validator.MAX_SKILL_BODY_WORDS
    base_skills = (baseline or {}).get("skills", {})

    for name, values in sorted(metrics["skills"].items()):
        words = values["body_words"]
        if words > ceiling:
            findings.append(
                finding(
                    "body-size",
                    "error",
                    f"{words} words exceeds the {ceiling}-word ceiling",
                    skill=name,
                )
            )
        previous = base_skills.get(name, {}).get("body_words")
        if previous is not None and words - previous > settings["body_growth_words"]:
            findings.append(
                finding(
                    "body-growth",
                    "warn",
                    f"grew from {previous} to {words} words since the baseline "
                    f"(+{words - previous}, threshold {settings['body_growth_words']})",
                    skill=name,
                )
            )
        if values["description_chars"] > settings["description_max_chars"]:
            findings.append(
                finding(
                    "description-length",
                    "warn",
                    f"description is {values['description_chars']} characters "
                    f"(limit {settings['description_max_chars']})",
                    skill=name,
                )
            )
        old = base_skills.get(name)
        if (
            old
            and old.get("description_hash") != values["description_hash"]
            and old.get("short_description_hash") == values["short_description_hash"]
            and old.get("readme_summary_hash") == values["readme_summary_hash"]
        ):
            findings.append(
                finding(
                    "summary-drift",
                    "info",
                    "description changed while short_description and the README "
                    "summary did not; confirm they still match",
                    skill=name,
                )
            )

    if metrics["routing_chars"] > metrics["routing_budget"]:
        findings.append(
            finding(
                "routing-budget",
                "error",
                f"routing metadata is {metrics['routing_chars']} characters, over the "
                f"{metrics['routing_budget']} budget",
            )
        )

    known_groups = set((baseline or {}).get("shared_sentence_keys", []))
    groups = metrics["shared_sentences"]
    new_groups = {key: item for key, item in groups.items() if key not in known_groups}
    for key, item in sorted(new_groups.items(), key=lambda pair: pair[1]["text"]):
        owners = ", ".join(item["skills"])
        findings.append(
            finding(
                "shared-sentence",
                "warn" if baseline else "info",
                f"{'new ' if baseline else ''}sentence shared by {owners}: "
                f"{item['text'][:140]}",
                location=key,
            )
        )

    for name, orphans in sorted(metrics["orphan_references"].items()):
        for relative in orphans:
            findings.append(
                finding(
                    "orphan-reference",
                    "warn",
                    f"{relative} is not linked from SKILL.md or another reference",
                    skill=name,
                    location=relative,
                )
            )
    for name, hits in sorted(metrics["bare_python"].items()):
        for location in hits:
            findings.append(
                finding(
                    "bare-script-path",
                    "warn",
                    "bare `python scripts/...` resolves against the user's project; "
                    'use python "<skill-dir>/scripts/..."',
                    skill=name,
                    location=location,
                )
            )
    for name, hits in sorted(metrics["milestones"].items()):
        for hit in hits:
            if next_major is not None and hit["major"] <= next_major:
                findings.append(
                    finding(
                        "version-milestone",
                        "warn",
                        f'"{hit["text"]}" names v{hit["major"]}, which is at or below '
                        f"the next major v{next_major}",
                        skill=name,
                        location=f"{hit['path']}:{hit['line']}",
                    )
                )
    for name, hits in sorted(metrics["stale_skill_names"].items()):
        for hit in hits:
            findings.append(
                finding(
                    "stale-skill-name",
                    "warn",
                    f"`{hit['name']}` is not a canonical skill name",
                    skill=name,
                    location=f"SKILL.md:{hit['line']}",
                )
            )
    for name, hits in sorted(metrics["stale_facts"].items()):
        for hit in hits:
            findings.append(
                finding(
                    "stale-fact",
                    "warn",
                    f'"{hit["text"]}" is {hit["age_days"]} days old '
                    f"(limit {settings['stale_fact_days']}); re-verify or drop the date",
                    skill=name,
                    location=f"{hit['path']}:{hit['line']}",
                )
            )

    known_pairs = set((baseline or {}).get("near_duplicate_pairs", []))
    for item in metrics["near_duplicates"]:
        if item["pair"] in known_pairs:
            continue
        findings.append(
            finding(
                "near-duplicate",
                "warn" if baseline else "info",
                f"{'new ' if baseline else ''}near-duplicate files "
                f"(containment {item['containment']}, {item['shared']} shared 6-grams): "
                f"{item['pair']}",
            )
        )
    for key, names in metrics["yaml_outliers"].items():
        findings.append(
            finding(
                "yaml-outlier",
                "info",
                f"agents/openai.yaml key `{key}` appears in only {len(names)} skill(s): "
                + ", ".join(names),
            )
        )

    findings.sort(
        key=lambda item: (
            SEVERITY_ORDER[item["severity"]],
            item["metric"],
            item["skill"] or "",
            item["location"] or "",
            item["message"],
        )
    )
    return findings


def delta_scope(
    repo_root: Path, baseline_commit: str | None, canonical: set[str], source_text: dict[str, str]
) -> dict[str, Any]:
    """Skills whose canonical files changed since the last-check commit, plus neighbours."""
    if not baseline_commit:
        return {"commit": None, "available": False, "changed": [], "neighbours": []}
    tracked = git(
        repo_root, "diff", "--name-only", baseline_commit, "--", "agent-plugins/skills"
    )
    if tracked is None:
        return {"commit": baseline_commit, "available": False, "changed": [], "neighbours": []}
    untracked = (
        git(
            repo_root,
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            "agent-plugins/skills",
        )
        or ""
    )
    changed: set[str] = set()
    for line in (tracked + "\n" + untracked).splitlines():
        parts = line.strip().split("/")
        if len(parts) >= 3 and parts[0] == "agent-plugins" and parts[1] == "skills":
            changed.add(parts[2])
    neighbours: set[str] = set()
    for name in changed & canonical:
        text = source_text.get(name, "")
        neighbours.update(
            token
            for token in re.findall(r"`([a-z][a-z0-9-]*)`", text)
            if token in canonical and token != name
        )
    return {
        "commit": baseline_commit,
        "available": True,
        "changed": sorted(changed),
        "removed": sorted(changed - canonical),
        "neighbours": sorted(neighbours - changed),
    }


def run_check(
    repo_root: Path, ledger: dict[str, Any], today: date
) -> dict[str, Any]:
    settings = ledger["settings"]
    metrics = compute_metrics(repo_root, settings, today)
    state = due_state(repo_root, ledger, project=True)
    baseline = ledger.get("baseline")
    findings = evaluate(metrics, settings, baseline, state["next_major"])
    last = state["last_check"] or {}
    source_root = (repo_root / wrappers.DEFAULT_SOURCE_DIR).resolve()
    skills = wrappers.discover_skills(source_root, [])
    delta = delta_scope(
        repo_root,
        last.get("commit"),
        {skill.name for skill in skills},
        {skill.name: skill.body for skill in skills},
    )
    return {
        "baseline": baseline is not None,
        "last_check": state["last_check"],
        "next_release_version": state["next_release_version"],
        "findings": findings,
        "summary": {
            severity: sum(1 for item in findings if item["severity"] == severity)
            for severity in SEVERITY_ORDER
        },
        "metrics": {
            "skill_count": metrics["skill_count"],
            "routing_chars": metrics["routing_chars"],
            "routing_budget": metrics["routing_budget"],
            "largest_bodies": sorted(
                ((values["body_words"], name) for name, values in metrics["skills"].items()),
                reverse=True,
            )[:5],
            "shared_sentence_groups": len(metrics["shared_sentences"]),
            "near_duplicate_pairs": len(metrics["near_duplicates"]),
        },
        "delta": delta,
        "_metrics": metrics,
    }


def render_check(result: dict[str, Any], *, limit: int = 12) -> str:
    metrics = result["metrics"]
    last = result["last_check"]
    if result["baseline"] and last:
        header = (
            f"Baseline: v{last.get('major')} {last.get('kind')} on {last.get('date')} "
            f"(commit {str(last.get('commit') or 'unknown')[:12]})"
        )
    else:
        header = (
            "Baseline: none recorded. Growth and new-group comparisons are skipped; "
            "every shared sentence and near-duplicate pair is listed as info."
        )
    lines = [
        header,
        f"Skills: {metrics['skill_count']}; routing metadata "
        f"{metrics['routing_chars']}/{metrics['routing_budget']} characters",
        "Largest bodies: "
        + ", ".join(f"{name} {words}" for words, name in metrics["largest_bodies"]),
        f"Next release version: {result['next_release_version'] or 'unknown'}",
        "",
    ]
    by_metric: dict[str, list[dict[str, Any]]] = {}
    for item in result["findings"]:
        by_metric.setdefault(item["metric"], []).append(item)
    ordered = sorted(
        by_metric.items(),
        key=lambda pair: (SEVERITY_ORDER[pair[1][0]["severity"]], pair[0]),
    )
    for metric, items in ordered:
        lines.append(f"{metric} ({len(items)})")
        for item in items[:limit]:
            where = " ".join(
                part for part in (item["skill"], item["location"]) if part
            )
            lines.append(
                f"  [{item['severity'].upper()}] "
                + (f"{where}: " if where else "")
                + item["message"]
            )
        if len(items) > limit:
            lines.append(f"  ... {len(items) - limit} more (use --format json for all)")
    if not ordered:
        lines.append("No findings.")
    delta = result["delta"]
    lines.append("")
    if delta["available"]:
        lines.append(f"Delta review scope since {str(delta['commit'])[:12]}")
        lines.append(
            "  changed skills: " + (", ".join(delta["changed"]) or "none")
        )
        lines.append(
            "  neighbours named in them: " + (", ".join(delta["neighbours"]) or "none")
        )
        if delta.get("removed"):
            lines.append("  removed skills: " + ", ".join(delta["removed"]))
    else:
        lines.append(
            "Delta review scope: unavailable (no recorded commit, or it is not in this "
            "clone). Review the skills changed in the releases since the last check."
        )
    summary = result["summary"]
    lines.append("")
    lines.append(
        f"Summary: {summary['error']} error, {summary['warn']} warn, {summary['info']} info"
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=SCRIPTS_DIR.parent,
        help="Repository root. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=DEFAULT_LEDGER,
        help="Ledger path, relative to --repo-root. Defaults to docs/skill-health.json.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    due = sub.add_parser("due", help="Report whether a healthcheck is due. Writes nothing.")
    due.add_argument("--format", choices=("text", "json"), default="text")

    check = sub.add_parser("check", help="Compute metrics and findings. Writes nothing.")
    check.add_argument("--format", choices=("text", "json"), default="text")
    check.add_argument("--today", help="Reference date, YYYY-MM-DD.")
    check.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when any error or warn finding remains.",
    )

    record = sub.add_parser(
        "record", help="Write the new baseline and check entry to the ledger."
    )
    record.add_argument("--kind", choices=CHECK_KINDS, default="delta-review")
    record.add_argument("--reference", default="", help="What the check covered.")
    record.add_argument("--notes", default="")
    record.add_argument(
        "--open-item",
        action="append",
        default=[],
        help="A finding left open. Repeat for several. Replaces the previous list.",
    )
    record.add_argument("--version", help="Release version to record. Defaults to the next release.")
    record.add_argument("--commit", help="Commit to record. Defaults to HEAD.")
    record.add_argument("--date", help="Check date, YYYY-MM-DD. Defaults to today.")
    record.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the ledger that would be written without writing it.",
    )
    return parser.parse_args(argv)


def parse_date_arg(raw: str | None, label: str) -> date:
    if not raw:
        return date.today()
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        raise HealthError(f"{label} must be YYYY-MM-DD: {raw!r}") from exc


def command_due(args: argparse.Namespace, repo_root: Path, ledger: dict[str, Any]) -> int:
    state = due_state(repo_root, ledger)
    if args.format == "json":
        print(json.dumps(state, indent=2, ensure_ascii=False))
    else:
        print(render_due(state))
    return 0


def command_check(args: argparse.Namespace, repo_root: Path, ledger: dict[str, Any]) -> int:
    result = run_check(repo_root, ledger, parse_date_arg(args.today, "--today"))
    result.pop("_metrics")
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render_check(result))
    failing = result["summary"]["error"] + result["summary"]["warn"]
    return 1 if args.strict and failing else 0


def command_record(
    args: argparse.Namespace, repo_root: Path, ledger_path: Path, ledger: dict[str, Any]
) -> int:
    today = parse_date_arg(args.date, "--date")
    state = due_state(repo_root, ledger)
    version = version_core(args.version) if args.version else state["next_release_version"]
    if not version:
        raise HealthError(
            "Cannot determine the release version to record; pass --version X.Y.Z."
        )
    commit = args.commit or (git(repo_root, "rev-parse", "HEAD") or "").strip() or None
    dirty = bool((git(repo_root, "status", "--porcelain") or "").strip())
    metrics = compute_metrics(repo_root, ledger["settings"], today)

    previous = ledger.get("last_check")
    history = list(ledger.get("history") or [])
    if isinstance(previous, dict):
        history.append(previous)
    entry = {
        "version": version,
        "major": version_tuple(version)[0],
        "commit": commit,
        "dirty": dirty,
        "date": today.isoformat(),
        "kind": args.kind,
        "reference": args.reference,
        "notes": args.notes,
    }
    updated = dict(ledger)
    updated["schema"] = LEDGER_SCHEMA
    updated["last_check"] = entry
    updated["baseline"] = baseline_from_metrics(metrics)
    updated["open_items"] = list(args.open_item)
    updated["history"] = history[-MAX_HISTORY:]

    interval = updated["settings"]["interval_majors"]
    due_at = entry["major"] + interval
    if args.dry_run:
        print(json.dumps(updated, indent=2, ensure_ascii=False))
        return 0
    write_ledger(ledger_path, updated)
    print(
        f"Recorded {args.kind} at v{version} (commit {str(commit or 'unknown')[:12]}"
        f"{', working tree dirty' if dirty else ''}) in "
        f"{ledger_path.relative_to(repo_root) if ledger_path.is_relative_to(repo_root) else ledger_path}."
    )
    print(f"The next healthcheck falls due when a release would become v{due_at}.")
    return 0


def run(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    ledger_path = args.ledger if args.ledger.is_absolute() else repo_root / args.ledger
    try:
        ledger = load_ledger(ledger_path)
        if args.command == "due":
            return command_due(args, repo_root, ledger)
        if args.command == "check":
            return command_check(args, repo_root, ledger)
        return command_record(args, repo_root, ledger_path, ledger)
    except (HealthError, wrappers.GenerationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: filesystem operation failed: {exc}", file=sys.stderr)
        return 1


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
