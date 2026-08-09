#!/usr/bin/env python3
"""Validate canonical skill packages without third-party dependencies."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Iterable, Sequence

import generate_skill_wrappers as wrappers

ALLOWED_FRONTMATTER_KEYS = {"name", "description"}
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_ENTRY_RE = re.compile(r"^([A-Za-z0-9_-]+):[ ]+(.+)$")
MAPPING_ENTRY_RE = re.compile(r"^  ([A-Za-z0-9_-]+):[ ]*(.*?)\s*$")
TOC_RE = re.compile(r"^##\s+(?:Table of [Cc]ontents|Contents)\s*$")
REQUIRED_ACTIVATION_CATEGORIES = {
    "direct",
    "indirect",
    "incomplete",
    "negative",
    "overlap",
}
MEMORY_SKILLS = ("audit-memory", "create-memory", "ingest-memory", "update-memory")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root. Defaults to the parent of scripts/.",
    )
    return parser.parse_args(argv)


def decode_restricted_yaml_scalar(raw: str) -> str:
    """Decode the portable scalar subset accepted in canonical frontmatter."""
    if not raw or raw != raw.strip() or "\t" in raw:
        raise ValueError("must be a non-empty scalar without tabs or edge whitespace")
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid double-quoted scalar: {exc.msg}") from exc
        if not isinstance(value, str):
            raise ValueError("must decode to a string")
        return value
    if raw.startswith("'"):
        if len(raw) < 2 or not raw.endswith("'"):
            raise ValueError("unterminated single-quoted scalar")
        inner = raw[1:-1]
        if "'" in inner.replace("''", ""):
            raise ValueError("single quotes inside a quoted scalar must be doubled")
        return inner.replace("''", "'")
    if raw[0] in "-?:,[]{}#&*!|>'\"%@`":
        raise ValueError("unsupported YAML indicator at the start of a plain scalar")
    if re.search(r":(?:\s|$)|\s#", raw):
        raise ValueError("ambiguous YAML mapping or comment syntax in plain scalar")
    if raw.casefold() in {
        "null",
        "true",
        "false",
        "yes",
        "no",
        "on",
        "off",
        "~",
    } or re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", raw):
        raise ValueError("plain scalar would not be interpreted portably as a string")
    return raw


def parse_portable_frontmatter(
    frontmatter: str,
) -> tuple[dict[str, str], list[str], list[str]]:
    """Parse and completely validate the restricted name/description mapping."""
    fields: dict[str, str] = {}
    keys: list[str] = []
    errors: list[str] = []
    if not frontmatter:
        return fields, keys, errors

    normalized = frontmatter.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.splitlines()
    if len(lines) < 3 or lines[0] != "---" or lines[-1] != "---":
        return fields, keys, ["frontmatter delimiters must be exact `---` lines"]

    for line_number, line in enumerate(lines[1:-1], start=2):
        if not line or line.lstrip().startswith("#"):
            continue
        if line[0].isspace():
            errors.append(
                f"line {line_number}: nested or indented frontmatter is not supported"
            )
            continue
        match = FRONTMATTER_ENTRY_RE.fullmatch(line)
        if not match:
            errors.append(
                f"line {line_number}: expected an unindented `name:` or "
                "`description:` string entry"
            )
            continue
        key, raw_value = match.groups()
        keys.append(key)
        if key in fields:
            errors.append(f"line {line_number}: duplicate frontmatter key {key!r}")
            continue
        try:
            fields[key] = decode_restricted_yaml_scalar(raw_value)
        except ValueError as exc:
            errors.append(f"line {line_number}: {key}: {exc}")
    return fields, keys, errors


def direct_mapping_entries(
    text: str, section: str
) -> tuple[dict[str, str], bool, list[str]]:
    """Return direct scalar children of one exact top-level YAML mapping."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    starts = [index for index, line in enumerate(lines) if line == f"{section}:"]
    if not starts:
        return {}, False, []
    errors: list[str] = []
    if len(starts) > 1:
        errors.append(f"duplicate top-level {section} mapping")

    start = starts[0]
    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line and not line[0].isspace() and not line.startswith("#"):
            end = index
            break

    entries: dict[str, str] = {}
    for index in range(start + 1, end):
        line = lines[index]
        if not line or line.lstrip().startswith("#"):
            continue
        match = MAPPING_ENTRY_RE.fullmatch(line)
        if not match:
            errors.append(
                f"line {index + 1}: {section} entries must be direct two-space "
                "scalar children"
            )
            continue
        key, raw_value = match.groups()
        if key in entries:
            errors.append(f"line {index + 1}: duplicate {section}.{key} entry")
            continue
        entries[key] = raw_value
    return entries, True, errors


def validate_openai_yaml(skill: wrappers.SourceSkill) -> list[str]:
    errors: list[str] = []
    metadata_path = skill.directory / "agents" / "openai.yaml"
    prefix = f"{skill.name}/agents/openai.yaml"
    if not metadata_path.is_file():
        return [f"{prefix}: missing recommended Codex UI metadata"]

    try:
        text = metadata_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        return [f"{prefix}: not valid UTF-8: {exc}"]

    interface, has_interface, interface_errors = direct_mapping_entries(
        text, "interface"
    )
    errors.extend(f"{prefix}: {error}" for error in interface_errors)
    if not has_interface:
        errors.append(f"{prefix}: missing interface mapping")

    values: dict[str, str | None] = {}
    for key in ("display_name", "short_description", "default_prompt"):
        raw_value = interface.get(key)
        if raw_value is None:
            values[key] = None
            errors.append(f"{prefix}: interface.{key} must be present and quoted")
            continue
        if not raw_value.startswith(("\"", "'")):
            values[key] = None
            errors.append(f"{prefix}: interface.{key} must be quoted")
            continue
        try:
            values[key] = decode_restricted_yaml_scalar(raw_value)
        except ValueError as exc:
            values[key] = None
            errors.append(f"{prefix}: interface.{key}: {exc}")

    short_description = values["short_description"]
    if short_description is not None and not 25 <= len(short_description) <= 64:
        errors.append(
            f"{prefix}: short_description must be 25-64 characters "
            f"(found {len(short_description)})"
        )

    default_prompt = values["default_prompt"]
    if default_prompt is not None and f"${skill.name}" not in default_prompt:
        errors.append(f"{prefix}: default_prompt must mention ${skill.name}")

    policy, _has_policy, policy_errors = direct_mapping_entries(text, "policy")
    errors.extend(f"{prefix}: {error}" for error in policy_errors)
    implicit = policy.get("allow_implicit_invocation")
    if implicit is not None and implicit not in {"true", "false"}:
        errors.append(
            f"{prefix}: policy.allow_implicit_invocation must be an unquoted boolean"
        )
    return errors


def validate_reference_navigation(skill: wrappers.SourceSkill) -> list[str]:
    errors: list[str] = []
    references = skill.directory / "references"
    if not references.is_dir():
        return errors
    for path in sorted(references.rglob("*.md")):
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        if len(lines) <= 100:
            continue
        if not any(TOC_RE.match(line.strip()) for line in lines[:50]):
            relative = path.relative_to(skill.directory).as_posix()
            errors.append(
                f"{skill.name}/{relative}: references over 100 lines need an early TOC"
            )
    return errors


def validate_python_scripts(skill: wrappers.SourceSkill) -> list[str]:
    errors: list[str] = []
    scripts = skill.directory / "scripts"
    if not scripts.is_dir():
        return errors
    for path in sorted(scripts.rglob("*.py")):
        relative = path.relative_to(skill.directory).as_posix()
        try:
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            errors.append(f"{skill.name}/{relative}: invalid Python: {exc}")
    return errors


def validate_skill(skill: wrappers.SourceSkill) -> list[str]:
    errors: list[str] = []
    prefix = skill.name
    fields, keys, frontmatter_errors = parse_portable_frontmatter(skill.frontmatter)

    if not skill.frontmatter:
        errors.append(f"{prefix}/SKILL.md: missing YAML frontmatter")
    errors.extend(
        f"{prefix}/SKILL.md: {error}" for error in frontmatter_errors
    )
    if set(keys) != ALLOWED_FRONTMATTER_KEYS or len(keys) != 2:
        errors.append(
            f"{prefix}/SKILL.md: frontmatter must contain exactly name and description; "
            f"found {keys}"
        )
    declared_name = fields.get("name")
    if declared_name != skill.name:
        errors.append(
            f"{prefix}/SKILL.md: frontmatter name {declared_name!r} does not "
            f"match directory"
        )
    if not SKILL_NAME_RE.fullmatch(skill.name) or len(skill.name) > 63:
        errors.append(f"{prefix}: invalid skill directory name")
    description = fields.get("description")
    if not description:
        errors.append(f"{prefix}/SKILL.md: missing description")
    elif not 40 <= len(description) <= 1024:
        errors.append(
            f"{prefix}/SKILL.md: description should be 40-1024 characters "
            f"(found {len(description)})"
        )
    if len(skill.body.splitlines()) > 500:
        errors.append(f"{prefix}/SKILL.md: body exceeds the 500-line guidance")
    if (skill.directory / "README.md").exists():
        errors.append(f"{prefix}/README.md: extraneous skill-local README")

    try:
        wrappers.validate_no_symlinks(skill)
    except wrappers.GenerationError as exc:
        errors.append(str(exc))
        return errors
    errors.extend(f"{prefix}: {warning}" for warning in wrappers.validate_local_links(skill))
    errors.extend(validate_openai_yaml(skill))
    errors.extend(validate_reference_navigation(skill))
    errors.extend(validate_python_scripts(skill))
    return errors


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_memory_family(source_root: Path) -> list[str]:
    errors: list[str] = []
    contract = Path("references/memory-contract.md")
    contract_paths = [source_root / skill / contract for skill in MEMORY_SKILLS]
    missing_contracts = [path for path in contract_paths if not path.is_file()]
    if missing_contracts:
        rendered = ", ".join(path.as_posix() for path in missing_contracts)
        errors.append(f"memory family: missing shared contract(s): {rendered}")
    elif len({file_digest(path) for path in contract_paths}) != 1:
        errors.append(
            "memory family: references/memory-contract.md copies must remain "
            "byte-identical"
        )

    shared_validator = source_root.parent / "shared" / "memory" / "validate_memory.py"
    shared_root = source_root.parent / "shared"
    shared_memory_root = shared_root / "memory"
    if (
        shared_root.is_symlink()
        or shared_memory_root.is_symlink()
        or shared_validator.is_symlink()
        or not shared_validator.is_file()
    ):
        errors.append(
            "memory family: missing regular canonical shared/memory/validate_memory.py"
        )
    else:
        try:
            ast.parse(
                shared_validator.read_text(encoding="utf-8-sig"),
                filename=str(shared_validator),
            )
        except (SyntaxError, UnicodeDecodeError) as exc:
            errors.append(f"memory family: invalid shared validator Python: {exc}")

    redundant = [
        source_root / skill / "scripts" / "validate_memory.py"
        for skill in MEMORY_SKILLS
        if (source_root / skill / "scripts" / "validate_memory.py").exists()
        or (source_root / skill / "scripts" / "validate_memory.py").is_symlink()
    ]
    if redundant:
        rendered = ", ".join(path.as_posix() for path in redundant)
        errors.append(
            "memory family: remove redundant canonical validator copies; "
            f"found {rendered}"
        )
    return errors


def validate_activation_cases(repo_root: Path, skill_names: Iterable[str]) -> list[str]:
    errors: list[str] = []
    path = repo_root / "tests" / "fixtures" / "activation_cases.json"
    if not path.is_file():
        return ["tests/fixtures/activation_cases.json: missing activation fixture"]
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"{path.as_posix()}: invalid JSON: {exc}"]
    if not isinstance(data, list):
        return [f"{path.as_posix()}: expected a JSON array"]

    known = set(skill_names)
    categories_by_skill = {name: set() for name in known}
    ids: set[str] = set()
    for index, case in enumerate(data):
        location = f"activation case #{index + 1}"
        if not isinstance(case, dict):
            errors.append(f"{location}: expected an object")
            continue
        case_id = case.get("id")
        skill = case.get("skill")
        category = case.get("category")
        prompt = case.get("prompt")
        expected = case.get("expected_skills")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{location}: missing string id")
        elif case_id in ids:
            errors.append(f"{location}: duplicate id {case_id!r}")
        else:
            ids.add(case_id)
        if skill not in known:
            errors.append(f"{location}: unknown primary skill {skill!r}")
            continue
        if category not in REQUIRED_ACTIVATION_CATEGORIES:
            errors.append(f"{location}: invalid category {category!r}")
        else:
            categories_by_skill[skill].add(category)
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{location}: prompt must be a non-empty string")
        if not isinstance(expected, list) or any(item not in known for item in expected):
            errors.append(f"{location}: expected_skills must contain only known skills")
        elif category in {"direct", "indirect", "incomplete"} and skill not in expected:
            errors.append(f"{location}: positive case must expect its primary skill")
        elif category == "negative" and skill in expected:
            errors.append(f"{location}: negative case must not expect its primary skill")

    for skill, categories in sorted(categories_by_skill.items()):
        missing = REQUIRED_ACTIVATION_CATEGORIES - categories
        if missing:
            errors.append(
                f"activation cases: {skill} is missing {', '.join(sorted(missing))}"
            )
    return errors


def validate_repository(repo_root: Path) -> list[str]:
    source_root = repo_root / "agent-plugins" / "skills"
    errors: list[str] = []
    try:
        skills = wrappers.discover_skills(source_root, [])
        for skill in skills:
            errors.extend(validate_skill(skill))
    except wrappers.GenerationError as exc:
        errors.append(str(exc))
        return errors

    routing_budget = sum(
        len(skill.name) + len(skill.description or "") for skill in skills
    )
    if routing_budget > 8000:
        errors.append(
            "canonical routing metadata exceeds the 8,000-character catalog budget "
            f"({routing_budget})"
        )

    errors.extend(validate_memory_family(source_root))
    errors.extend(validate_activation_cases(repo_root, (skill.name for skill in skills)))
    for required_notice in (
        repo_root / "THIRD_PARTY_NOTICES.md",
        source_root / "code-review" / "LICENSE.addyosmani-agent-skills",
        source_root / "stop-slop" / "LICENSE",
    ):
        if not required_notice.is_file():
            errors.append(
                f"{required_notice.relative_to(repo_root).as_posix()}: "
                "missing retained third-party notice"
            )
    return errors


def run(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    errors = validate_repository(args.repo_root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Skill validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print("Skill validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
