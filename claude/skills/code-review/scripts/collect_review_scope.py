#!/usr/bin/env python3
"""Collect a deterministic local Git review scope as JSON."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Sequence


HUNK_RE = re.compile(
    r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@"
)


class ScopeError(RuntimeError):
    """Raised when a trustworthy review scope cannot be established."""


def run_git(
    repo: Path,
    args: Sequence[str],
    *,
    check: bool = True,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ScopeError(f"git {' '.join(args)} failed: {detail}")
    return result


def git_root(candidate: Path) -> Path:
    result = run_git(candidate, ["rev-parse", "--show-toplevel"])
    return Path(result.stdout.strip()).resolve()


def verify_ref(repo: Path, ref: str) -> str | None:
    result = run_git(
        repo,
        ["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def discover_base(repo: Path, explicit: str | None) -> tuple[str, str]:
    if explicit:
        commit = verify_ref(repo, explicit)
        if not commit:
            raise ScopeError(f"comparison base does not resolve to a commit: {explicit}")
        return explicit, commit

    remotes = run_git(repo, ["remote"], check=False).stdout.splitlines()
    for remote in remotes:
        symbolic = run_git(
            repo,
            ["symbolic-ref", "--quiet", f"refs/remotes/{remote}/HEAD"],
            check=False,
        )
        if symbolic.returncode == 0:
            ref = symbolic.stdout.strip()
            commit = verify_ref(repo, ref)
            if commit:
                return ref, commit

    for ref in ("main", "master", "develop"):
        commit = verify_ref(repo, ref)
        if commit:
            return ref, commit

    raise ScopeError(
        "no comparison base found; pass --base from the user or pull request metadata"
    )


def normalize_paths(repo: Path, values: Sequence[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        candidate = Path(value)
        resolved = candidate.resolve() if candidate.is_absolute() else (repo / candidate).resolve()
        try:
            relative = resolved.relative_to(repo)
        except ValueError as exc:
            raise ScopeError(f"path filter escapes the repository: {value}") from exc
        normalized.append(relative.as_posix() or ".")
    return normalized


def path_args(paths: Sequence[str]) -> list[str]:
    return ["--", *paths] if paths else []


def has_diff(repo: Path, args: Sequence[str]) -> bool:
    result = run_git(repo, ["diff", "--quiet", *args], check=False)
    if result.returncode not in (0, 1):
        raise ScopeError(result.stderr.strip() or "git diff --quiet failed")
    return result.returncode == 1


def name_status(repo: Path, baseline: str, paths: Sequence[str]) -> list[dict[str, str]]:
    result = run_git(
        repo,
        ["diff", "--name-status", "-z", baseline, *path_args(paths)],
    )
    tokens = result.stdout.split("\0")
    if tokens and not tokens[-1]:
        tokens.pop()

    entries: list[dict[str, str]] = []
    index = 0
    while index < len(tokens):
        status = tokens[index]
        index += 1
        if not status:
            continue
        kind = status[0]
        if kind in {"R", "C"}:
            if index + 1 >= len(tokens):
                raise ScopeError("unexpected truncated rename/copy record from git diff")
            old_path, new_path = tokens[index], tokens[index + 1]
            index += 2
            entries.append(
                {"status": status, "old_path": old_path, "path": new_path}
            )
        else:
            if index >= len(tokens):
                raise ScopeError("unexpected truncated path record from git diff")
            entries.append({"status": status, "path": tokens[index]})
            index += 1
    return entries


def hunks_for(repo: Path, baseline: str, path: str) -> list[dict[str, int]]:
    result = run_git(
        repo,
        [
            "diff",
            "--no-ext-diff",
            "--no-color",
            "--unified=0",
            baseline,
            "--",
            path,
        ],
    )
    hunks: list[dict[str, int]] = []
    for line in result.stdout.splitlines():
        match = HUNK_RE.match(line)
        if not match:
            continue
        old_start, old_count, new_start, new_count = match.groups()
        hunks.append(
            {
                "old_start": int(old_start),
                "old_count": int(old_count or "1"),
                "new_start": int(new_start),
                "new_count": int(new_count or "1"),
            }
        )
    return hunks


def untracked_files(repo: Path, paths: Sequence[str]) -> list[dict[str, object]]:
    result = run_git(
        repo,
        ["ls-files", "--others", "--exclude-standard", "-z", *path_args(paths)],
    )
    entries: list[dict[str, object]] = []
    for relative in filter(None, result.stdout.split("\0")):
        full_path = repo / relative
        if full_path.is_symlink():
            entries.append(
                {
                    "status": "untracked",
                    "path": Path(relative).as_posix(),
                    "tracked": False,
                    "binary": False,
                    "symlink": True,
                    "link_target": os.readlink(full_path),
                    "line_count": 1,
                    "hunks": [
                        {
                            "old_start": 0,
                            "old_count": 0,
                            "new_start": 1,
                            "new_count": 1,
                        }
                    ],
                }
            )
            continue
        binary = False
        newline_count = 0
        last_byte = b""
        with full_path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                if b"\0" in chunk:
                    binary = True
                    break
                newline_count += chunk.count(b"\n")
                last_byte = chunk[-1:]
        line_count = 0 if binary or not last_byte else newline_count + (last_byte != b"\n")
        entries.append(
            {
                "status": "untracked",
                "path": Path(relative).as_posix(),
                "tracked": False,
                "binary": binary,
                "line_count": int(line_count),
                "hunks": []
                if binary or line_count == 0
                else [
                    {
                        "old_start": 0,
                        "old_count": 0,
                        "new_start": 1,
                        "new_count": int(line_count),
                    }
                ],
            }
        )
    return entries


def collect(args: argparse.Namespace) -> dict[str, object]:
    root = git_root(Path(args.repo).resolve())
    filters = normalize_paths(root, args.path)
    head = verify_ref(root, "HEAD")

    if head:
        base_ref, base_commit = discover_base(root, args.base)
        merge_base = run_git(root, ["merge-base", base_commit, head]).stdout.strip()
        committed = has_diff(root, [merge_base, head, *path_args(filters)])
    else:
        if args.base:
            raise ScopeError("cannot compare --base in a repository without HEAD")
        merge_base = run_git(root, ["mktree"], input_text="").stdout.strip()
        base_ref, base_commit, committed = "(empty repository)", merge_base, False

    tracked = name_status(root, merge_base, filters)
    for entry in tracked:
        entry["tracked"] = True
        entry["hunks"] = hunks_for(root, merge_base, entry["path"])

    untracked = untracked_files(root, filters)
    branch = run_git(
        root, ["symbolic-ref", "--quiet", "--short", "HEAD"], check=False
    ).stdout.strip() or None

    return {
        "schema_version": 1,
        "repository_root": str(root),
        "branch": branch,
        "head": head,
        "base_ref": base_ref,
        "base_commit": base_commit,
        "merge_base": merge_base,
        "path_filters": filters,
        "change_sources": {
            "committed": committed,
            "staged": has_diff(root, ["--cached", *path_args(filters)]),
            "unstaged": has_diff(root, path_args(filters)),
            "untracked": bool(untracked),
        },
        "files": [*tracked, *untracked],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", default=".", help="Path inside the target Git repository"
    )
    parser.add_argument(
        "--base",
        help="Verified base ref or commit; pass the PR base when reviewing a PR",
    )
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Repository-relative file or directory filter; repeat as needed",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = collect(args)
    except (OSError, ScopeError) as exc:
        print(f"collect_review_scope: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2 if args.pretty else None,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
