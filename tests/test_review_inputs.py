"""Exercise compact helper output against the ordinary CLI contracts."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "agent-plugins/skills/code-review/scripts"


def tool(name, *args, stdin=None):
    return subprocess.run([sys.executable, str(SCRIPTS / name), *args],
                          input=stdin, capture_output=True, encoding="utf-8")


def outputs(name, *args):
    result = tool(name, *args)
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class ReviewInputs(unittest.TestCase):
    def test_asset_cli_preserves_missing_ids_and_empty_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.git(repo, "init", "-q")
            self.commit(repo, {"AGENTS.md": "Minimal instructions.\n", "rules/café.md": "- **RULE-1** Check labels.\n"})
            for extra in ([], ["--rules-only", "--no-memory"]):
                args = ["--repo", tmp, "--asset", "missing.md", *extra]
                default = outputs("review_assets.py", *args)
                packet = outputs("review_assets.py", "--compact", *args)
                result = tool("review_assets.py", "--expand", "-", stdin=json.dumps(packet))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), default)
                self.assertIn("rules/café.md", default["rule_inventory"])
                self.assertEqual(default["rule_inventory"]["AGENTS.md"], [])
                self.assertNotIn("missing.md", default["rule_inventory"])
                self.assertTrue(any(row.get("error") for row in packet["assets"]))
            bad = tool("review_assets.py", "--expand", "-", stdin='{"format":"review-assets/2"}')
            self.assertEqual((bad.returncode, bad.stdout), (2, ""))

    @staticmethod
    def git(repo, *args):
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()

    def commit(self, repo, changes):
        for name, contents in changes.items():
            target = repo / name
            target.parent.mkdir(exist_ok=True, parents=True)
            target.write_text(contents, encoding="utf-8")
        self.git(repo, "add", "-A")
        self.git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgSign=false", "commit", "-qm", "fixture")
        return self.git(repo, "rev-parse", "HEAD")

    def test_scope_cli_preserves_live_inputs_and_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.git(repo, "init", "-q")
            base = self.commit(repo, {"file.txt": "base\n"})
            self.commit(repo, {"file.txt": "committed\n"})
            (repo / "staged.txt").write_text("staged")
            self.git(repo, "add", "staged.txt")
            (repo / "file.txt").write_text("unstaged")
            (repo / "new.txt").write_text("untracked")
            args = ["--repo", tmp, "--base", base]
            plain = outputs("collect_review_scope.py", *args)
            self.assertTrue(all(plain["change_sources"].values()))
            self.assertEqual(outputs("collect_review_scope.py", *args, "--pretty"), plain)
            compact = tool("collect_review_scope.py", *args, "--compact")
            self.assertEqual(compact.returncode, 0, compact.stderr)
            self.assertEqual(json.loads(compact.stdout), plain)
            self.assertNotIn('": ', compact.stdout)
            for mode in ([], ["--compact"]):
                bad = tool("collect_review_scope.py", "--repo", tmp, "--base", "missing", *mode)
                self.assertEqual((bad.returncode, bad.stdout), (2, ""))
                self.assertIn("does not resolve", bad.stderr)
