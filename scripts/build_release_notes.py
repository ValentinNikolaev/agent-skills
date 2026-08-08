#!/usr/bin/env python3
"""Build GitHub release notes for generated plugin releases."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Sequence


def run_git(args: Sequence[str], *, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        check=False,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise SystemExit(result.stderr.strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", choices=("claude", "codex", "all"), required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def previous_release_tag(platform: str, target: str) -> str | None:
    patterns = (
        ("v*", "agent-plugins-v*")
        if platform == "all"
        else (f"{platform}-v*",)
    )
    match_args = [
        argument for pattern in patterns for argument in ("--match", pattern)
    ]
    tag = run_git(
        ["describe", "--tags", *match_args, "--abbrev=0", f"{target}^"],
        check=False,
    )
    return tag or None


def changed_files(base: str, target: str) -> list[tuple[str, str]]:
    output = run_git(["diff", "--name-status", base, target])
    changes: list[tuple[str, str]] = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0]
            path = parts[-1]
            changes.append((status, path))
    return changes


def relevant_changes(
    changes: Sequence[tuple[str, str]],
    platform: str,
) -> list[tuple[str, str]]:
    if platform == "all":
        relevant_prefixes = (
            "agent-plugins/skills/",
            "claude/skills/",
            "codex/skills/",
        )
        relevant_files = {
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
            "README.md",
        }
    else:
        generated_prefix = f"{platform}/skills/"
        relevant_prefixes = ("agent-plugins/skills/", generated_prefix)
        relevant_files = {f".{platform}-plugin/plugin.json", "README.md"}
    return [
        (status, path)
        for status, path in changes
        if path.startswith(relevant_prefixes) or path in relevant_files
    ]


def skill_name_from_path(path: str, prefix: str) -> str | None:
    if not path.startswith(prefix):
        return None
    rest = path[len(prefix) :]
    return rest.split("/", 1)[0] if rest else None


def render_notes(platform: str, version: str, target: str) -> str:
    platform_label = {
        "claude": "Claude",
        "codex": "Codex",
        "all": "Agent plugins",
    }[platform]
    previous_tag = previous_release_tag(platform, target)
    base = previous_tag or f"{target}^"
    changes = relevant_changes(changed_files(base, target), platform)

    canonical_skills = sorted(
        {
            name
            for _status, path in changes
            if (name := skill_name_from_path(path, "agent-plugins/skills/"))
        }
    )
    generated_prefixes = (
        [(platform, f"{platform}/skills/")]
        if platform != "all"
        else [("claude", "claude/skills/"), ("codex", "codex/skills/")]
    )
    generated_skills = {
        name: sorted(
            {
                skill
                for _status, path in changes
                if (skill := skill_name_from_path(path, prefix))
            }
        )
        for name, prefix in generated_prefixes
    }
    metadata_files = (
        {f".{platform}-plugin/plugin.json", "README.md"}
        if platform != "all"
        else {
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
            "README.md",
        }
    )
    metadata_changes = [path for _status, path in changes if path in metadata_files]

    lines = [
        f"{platform_label} plugin {version}",
        "",
        "## What changed",
        "",
    ]
    if previous_tag:
        lines.append(f"Compared with `{previous_tag}`.")
    else:
        lines.append("No previous platform release tag was found, so this compares with the previous commit.")

    lines.extend(["", "## Skills", ""])
    if canonical_skills:
        lines.append("Canonical skill changes:")
        lines.extend(f"- `{skill}`" for skill in canonical_skills)
        lines.append("")
    generated_count = 0
    for generated_platform, skills in generated_skills.items():
        if not skills:
            continue
        generated_count += len(skills)
        label = generated_platform.capitalize()
        lines.append(f"Generated {label} skill changes:")
        lines.extend(f"- `{skill}`" for skill in skills)
        lines.append("")
    if not canonical_skills and not generated_count:
        lines.append("- No skill file changes detected in this comparison.")
        lines.append("")

    if metadata_changes:
        lines.append("Metadata and docs:")
        lines.extend(f"- `{path}`" for path in metadata_changes)
        lines.append("")

    lines.extend(["## Changed files", ""])
    if changes:
        for status, path in changes[:75]:
            lines.append(f"- `{status}` `{path}`")
        if len(changes) > 75:
            lines.append(f"- ...and {len(changes) - 75} more file(s).")
    else:
        lines.append("- No file changes detected.")

    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    notes = render_notes(args.platform, args.version, args.target)
    args.output.write_text(notes, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
