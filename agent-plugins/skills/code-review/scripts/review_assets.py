"""Resolve project review material at a specific revision using local Git objects."""

from __future__ import annotations

import argparse
from datetime import date
from functools import lru_cache
from hashlib import sha256
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess


def git(repo, *args):
    # A partial clone must not lazily fetch a missing rules blob.
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_ALLOW_PROTOCOL="")
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                            env=env, encoding="utf-8", errors="replace")
    return result.stdout if result.returncode == 0 else None


@lru_cache(maxsize=12)
def tree(repo, rev):
    raw = git(repo, "ls-tree", "-rz", "--full-tree", rev)
    if raw is None:
        raise ValueError(f"cannot read local Git tree at {repo} {rev}")
    entries = {}
    for line in filter(None, raw.split("\0")):
        meta, path = line.split("\t", 1)
        mode, _, oid = meta.split()
        entries[path] = (mode, oid)
    return entries


@lru_cache(maxsize=256)
def blob(repo, oid):
    return git(repo, "cat-file", "blob", oid)


def local_path(path):
    path = posixpath.normpath(path)
    if path in (".", "..") or path.startswith(("../", "/")) or ":" in path or "\\" in path:
        raise ValueError("rule pointer leaves its source repository")
    return path


def pointer(text):
    value = text.strip()
    if "\n" in value or "\r" in value:
        return None
    if value.startswith("@include "):
        return value[9:].strip().strip('"<>')
    if value.startswith("@") and not any(c.isspace() for c in value):
        return value[1:]
    if re.fullmatch(r"(?:\.{1,2}/[^\r\n]+|[\w.-]+(?:/[\w.-]+)+|[\w./-]+\.(?:md|txt|rst))", value):
        return value
    return None


def rule_labels(text):
    """Seed a checklist from labelled bullets, table rows or headings."""
    labels = []
    headings = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1].startswith(fence):
                fence = None
            continue
        if fence:
            continue
        label = re.match(r"^\s*(?:[-*|#]+\s*)?(?:\[[ xX]\]\s*)?[`*_]*(\b[A-Z][A-Z0-9_.-]*?-?\d+\b|\d+(?:\.\d+)*[.)])(?=[\s:`*_|.)-]|$)", line)
        if label:
            labels.append(label[1].rstrip(".)"))
        heading = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if heading:
            headings.append(heading[1])
    return list(dict.fromkeys(labels or headings))


def worktrees(repo):
    listing = git(repo, "worktree", "list", "--porcelain", "-z") or ""
    return [Path(item[9:]) for item in listing.split("\0") if item.startswith("worktree ")]


def origin_key(url):
    return url.strip().removesuffix(".git").rstrip("/")


class Resolver:
    def __init__(self, root, revision, siblings):
        self.root = root
        self.project = next(iter(worktrees(root)), root).resolve()
        resolved = git(root, "rev-parse", "--verify", "--end-of-options", revision + "^{commit}")
        if not resolved:
            raise ValueError(f"unavailable review revision: {revision}")
        self.head = resolved.strip()
        self.siblings = siblings

    @lru_cache(maxsize=None)
    def module(self, path, pin):
        config = git(self.root, "config", "--blob", self.head + ":.gitmodules",
                     "--get-regexp", r"^submodule\..*\.path$") or ""
        key = next((line.split(" ", 1)[0][:-5] for line in config.splitlines()
                    if line.partition(" ")[2] == path), None)
        url = (git(self.root, "config", "--blob", self.head + ":.gitmodules",
                   "--get", key + ".url") or "").strip() if key else ""
        basename = re.split(r"[:/]", origin_key(url))[-1]
        roots = worktrees(self.root)
        candidates = [(base / path, "initialized submodule") for base in [self.root, *roots]]
        suggestions = [*self.siblings]
        if basename and re.fullmatch(r"[\w.-]+", basename) and basename not in (".", ".."):
            suggestions.extend(base.parent / basename for base in [self.root, *roots])
        for sibling in dict.fromkeys(suggestions):
            if (sibling / ".git").exists():
                origin = git(sibling, "remote", "get-url", "origin") or ""
                matches_url = url and origin_key(origin) == origin_key(url)
                local_source = not origin and basename == sibling.name and url.endswith(sibling.name)
                matches_pin = sibling in self.siblings and git(sibling, "cat-file", "-e", pin + "^{commit}") is not None
                if matches_url or local_source or matches_pin:
                    candidates.extend((p, "sibling checkout") for p in [sibling, *worktrees(sibling)])
        # Deinitializing a submodule usually leaves its object database here.
        if key:
            name = local_path(key[len("submodule."):])
            admin = git(self.root, "rev-parse", "--path-format=absolute", "--git-path",
                        "modules/" + name)
            if admin and Path(admin.strip()).is_dir():
                candidates.append((Path(admin.strip()), "submodule objects"))
        candidates.append((self.root, "superproject objects"))
        stale = []
        for source, kind in dict.fromkeys(candidates):
            if kind.endswith(("submodule", "checkout")) and not (source / ".git").exists():
                continue
            if git(source, "cat-file", "-e", pin + "^{commit}") is not None:
                return source, pin, kind, ""
            if kind in ("initialized submodule", "sibling checkout"):
                tip = git(source, "rev-parse", "--verify", "HEAD")
                if tip:
                    stale.append((source, tip.strip(), kind))
        if stale:
            source, tip, kind = stale[0]
            return source, tip, kind, "source revision differs from the reviewed gitlink"
        raise ValueError(f"unresolved submodule {path} at {pin}")

    def resolve(self, logical):
        repo, rev, path = self.root, self.head, local_path(logical)
        row = {"path": logical, "method": "repository", "pointers": []}
        seen = set()
        while (repo, rev, path) not in seen and len(seen) < 40:
            seen.add((repo, rev, path))
            entries = tree(repo, rev)
            parts = path.split("/")
            for size in range(1, len(parts) + 1):
                prefix = "/".join(parts[:size])
                if prefix not in entries:
                    continue
                mode, oid = entries[prefix]
                suffix = parts[size:]
                if mode == "160000":
                    if "pin" in row:
                        raise ValueError(f"nested gitlink requires separate resolution: {prefix}")
                    repo, rev, method, warning = self.module(prefix, oid)
                    row.update(pin=oid, mount=prefix, method=method, warning=warning)
                    if warning:
                        changed = git(self.root, "log", "-1", "--format=%ct", self.head, "--", prefix)
                        supplied = git(repo, "log", "-1", "--format=%ct", rev)
                        if changed and supplied and int(supplied) < int(changed):
                            row["warning"] += "; predates the last pin change"
                    path = local_path("/".join(suffix) or "SKILL.md")
                    break
                content = blob(repo, oid)
                if content is None:
                    raise ValueError(f"unavailable local blob: {prefix}")
                target = content.strip() if mode == "120000" else pointer(content)
                if target:
                    row["pointers"].append(prefix)
                    path = local_path(posixpath.join(posixpath.dirname(prefix), target, *suffix))
                    break
                if suffix:
                    raise ValueError(f"rule pointer expected at {prefix}")
                row.update(source=str(repo), revision=rev, file=prefix, blob=oid)
                return row, content
            else:
                if path + "/SKILL.md" in entries:
                    path += "/SKILL.md"
                    continue
                raise ValueError(f"missing rule path: {logical} ({rev}:{path})")
        raise ValueError(f"cyclic or excessively nested rule pointer: {logical}")


def discovery_kind(path, mode):
    parts = PurePosixPath(path).parts
    name = parts[-1].lower()
    if name in ("agents.md", "claude.md") or ("rules" in parts and name.endswith((".md", ".mdc", ".txt", ".rst"))):
        return "rules"
    if ("skills" in parts or "agents" in parts) and (
        name == "skill.md" or mode == "120000" or "skills" in parts[-2:-1] or
        ("agents" in parts and name.endswith(".md"))
    ):
        return "reviewer"
    return None


def discovery_fingerprint(entries):
    digest = sha256()
    for path, (mode, oid) in entries.items():
        if mode == "160000" or path == ".gitmodules" or discovery_kind(path, mode):
            digest.update(f"{mode} {oid} {path}\0".encode())
    return digest.hexdigest()


def discover(resolver, extra):
    entries = tree(resolver.root, resolver.head)
    paths = set(extra)
    for path, (mode, _) in entries.items():
        parts = PurePosixPath(path).parts
        name = parts[-1].lower()
        kind = discovery_kind(path, mode)
        if kind == "rules":
            paths.add(path)
        skill_directory = len(parts) >= 2 and parts[-2] == "skills"
        if kind == "reviewer":
            logical = path + "/SKILL.md" if skill_directory and "." not in name else path
            try:
                _, content = resolver.resolve(logical)
            except ValueError:
                if "review" in path.lower():
                    paths.add(logical)
                continue
            description = re.search(r"(?im)^description:\s*(.*)$", content)
            if "review" in path.lower() or (description and "review" in description[1].lower()):
                paths.add(logical)
    return sorted(paths)


def inspect_assets(resolver, paths):
    rows, seen = [], set()
    queue = list(paths)
    while queue:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        try:
            row, content = resolver.resolve(path)
        except ValueError as exc:
            rows.append({"path": path, "error": str(exc)})
            continue
        rows.append(row)
        owner = posixpath.join(row.get("mount", ""), row["file"])
        for include in re.findall(r'(?m)^@(?:include[ \t]+)?([^\n\r ]+)[ \t]*$', content):
            queue.append(posixpath.normpath(posixpath.join(posixpath.dirname(owner), include.strip('"<>'))))
    return rows


def integrate(resolver, entry, extra=(), *, rules_only=False, memory_available=True, today=None):
    today = today or date.today()
    rows = None
    fingerprint = discovery_fingerprint(tree(resolver.root, resolver.head))
    if entry and entry.get("project") == str(resolver.project):
        try:
            age = (today - date.fromisoformat(entry["date"])).days
            old = entry["assets"]
            prior_fingerprint = entry.get("discovery_fingerprint")
            if not prior_fingerprint:
                # Older host entries predate the inventory stamp. Compare their recorded tree.
                prior_head = next((r["revision"] for r in old if r.get("method") == "repository"), None)
                if prior_head:
                    prior_fingerprint = discovery_fingerprint(tree(resolver.root, prior_head))
            if (0 <= age <= 30 and fingerprint == prior_fingerprint and isinstance(old, list)
                and all(r.get("mode") in ("rules-source", "invoke", "ignore") and r.get("reason") for r in old)
                and set(extra) <= {r["path"] for r in old}):
                checked = inspect_assets(resolver, [r["path"] for r in old])
                fields = ("file", "pin", "blob", "pointers", "method")
                if len(old) == len(checked) and all(
                    "error" not in new and all(new.get(k) == prev.get(k) for k in fields)
                    and (new["method"] == "repository" or new["source"] == prev["source"])
                    and (not new.get("pin") or new["revision"] == prev["revision"])
                    for new, prev in zip(checked, old)
                ):
                    rows = checked
        except (AttributeError, KeyError, TypeError, ValueError):
            pass
    cached = rows is not None
    if not cached:
        rows = inspect_assets(resolver, discover(resolver, extra))
    for i, row in enumerate(rows):
        if cached:
            row.update(mode=old[i]["mode"], reason=old[i]["reason"])
        else:
            row.update(mode="rules-source", reason="Read project guidance for applicable rules.")
        if rules_only and (row["mode"] == "invoke" or (not cached and "review" in row["path"].lower())):
            row.update(mode="rules-source", reason="Caller permits reading this asset only.")
    updated = dict(entry) if cached else {}
    # Per-invocation vetoes must not overwrite a standing host-memory decision.
    saved_assets = [dict(row, mode=prior["mode"], reason=prior["reason"])
                    for row, prior in zip(rows, old)] if cached else rows
    updated.update(project=str(resolver.project), discovery_fingerprint=fingerprint, assets=saved_assets,
                   date=entry["date"] if cached else today.isoformat(),
                   refresh="Recheck recorded paths, sources and pins; rediscover after 30 days.")
    updated.setdefault("required_pr_sections", [])
    updated.setdefault("consumer_repository", None)
    inventory = {}
    for row in rows:
        if row["mode"] != "ignore" and "blob" in row:
            inventory[row["path"]] = rule_labels(blob(Path(row["source"]), row["blob"]))
    return {"action": "reuse" if cached else "discover", "assets": rows,
            "rule_inventory": inventory,
            "memory": "available" if memory_available else "unavailable; entry not saved",
            "entry": updated if memory_available else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--revision", default="HEAD")
    parser.add_argument("--sibling", action="append", default=[], type=Path)
    parser.add_argument("--asset", action="append", default=[], help="Additional instruction-named path")
    parser.add_argument("--entry", type=Path, help="Host-exported code-review-integration JSON")
    parser.add_argument("--no-memory", action="store_true")
    parser.add_argument("--rules-only", action="store_true")
    args = parser.parse_args()
    try:
        root = Path(args.repo).resolve()
        entry = json.loads(args.entry.read_text(encoding="utf-8-sig")) if args.entry else None
        siblings = [p.resolve() for p in args.sibling]
        resolver = Resolver(root, args.revision, siblings)
        if isinstance(entry, dict) and entry.get("project") == str(resolver.project):
            siblings.extend(Path(r["source"]) for r in entry.get("assets", [])
                            if isinstance(r, dict) and r.get("method") == "sibling checkout" and r.get("source"))
        elif entry is not None:
            entry = None
        print(json.dumps(integrate(resolver, entry, args.asset, rules_only=args.rules_only,
                                   memory_available=not args.no_memory), indent=2))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"Cannot resolve review assets: {exc}\n")


if __name__ == "__main__":
    main()
