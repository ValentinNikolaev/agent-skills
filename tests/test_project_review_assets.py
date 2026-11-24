"""Exercise the reviewer/host handoff against disposable local Git histories."""

from datetime import date, timedelta
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "agent-plugins/skills/code-review/scripts/review_assets.py"
spec = importlib.util.spec_from_file_location("review_assets", SCRIPT)
assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assets)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def commit(repo, title):
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "-qm", title)
    return git(repo, "rev-parse", "HEAD")


class ReviewAssetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.rules = root / "handbook"
        self.repo = root / "library"
        for repo in (self.rules, self.repo):
            repo.mkdir()
            git(repo, "init", "-q")
        self.host_entry = root / "memory" / "code-review-integration.json"
        self.rules_url = "https://example.invalid/team/handbook.git"
        git(self.rules, "remote", "add", "origin", self.rules_url)
        (self.rules / "review").mkdir()
        (self.rules / "review/SKILL.md").write_text("# Review\n- [ ] **QA-2** Check the input.\n")
        self.pin = commit(self.rules, "Pinned rules")
        (self.rules / "review/SKILL.md").write_text("# Other review\n")
        commit(self.rules, "A different checkout revision")
        (self.repo / ".agents/skills").mkdir(parents=True)
        (self.repo / ".agents/skills/review").write_text("../../handbook/review")
        (self.repo / "rules").mkdir()
        (self.repo / "rules/tests.md").write_text("@include ../handbook/review/SKILL.md")
        (self.repo / "AGENTS.md").write_text("Use the included test rules.\n@rules/tests.md\n")
        (self.repo / ".gitmodules").write_text(
            f'[submodule "guide"]\n\tpath = handbook\n\turl = {self.rules_url}\n')
        commit(self.repo, "Project instructions")
        self.set_pin(self.pin)

    def set_pin(self, rev):
        git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{rev},handbook")
        git(self.repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", "Update rule pin")

    def resolver(self):
        return assets.Resolver(self.repo, "HEAD", [])

    def test_cold_then_warm_file_backed_host_and_caller_veto(self):
        result = assets.integrate(self.resolver(), None)
        self.assertEqual(result["action"], "discover")
        self.assertFalse((self.repo / "handbook/.git").exists())
        asset = next(r for r in result["assets"] if "skills/" in r["path"])
        self.assertEqual(asset["revision"], self.pin)
        self.assertEqual(asset["method"], "sibling checkout")
        self.assertEqual(result["rule_inventory"][asset["path"]], ["QA-2"])
        self.assertEqual(result["rule_inventory"]["rules/tests.md"], ["QA-2"])
        self.assertTrue(asset["pointers"])
        # The host owns this write and mode decision. The resolver only emits a proposal.
        asset.update(mode="invoke", reason="Project reviewer supplies an additional read-only pass.")
        self.host_entry.parent.mkdir()
        self.host_entry.write_text(json.dumps(result["entry"]))
        with patch.object(assets, "discover", side_effect=AssertionError("rediscovery")):
            for veto, mode in ((False, "invoke"), (True, "rules-source")):
                memory = json.loads(self.host_entry.read_text())
                warm = assets.integrate(self.resolver(), memory, rules_only=veto)
                self.assertEqual(warm["action"], "reuse")
                self.assertEqual(next(r["mode"] for r in warm["assets"] if r["path"] == asset["path"]), mode)
                self.assertEqual(next(r["mode"] for r in warm["entry"]["assets"] if r["path"] == asset["path"]), "invoke")
        self.assertEqual(json.loads(self.host_entry.read_text())["assets"][0]["mode"], "invoke")

    def test_stale_pin_removed_path_and_expired_entries_rediscover(self):
        memory = assets.integrate(self.resolver(), None)["entry"]
        self.set_pin(git(self.rules, "rev-parse", "HEAD"))
        self.assertEqual(assets.integrate(self.resolver(), memory)["action"], "discover")
        memory = assets.integrate(self.resolver(), None)["entry"]
        memory["date"] = (date.today() - timedelta(days=31)).isoformat()
        self.assertEqual(assets.integrate(self.resolver(), memory)["action"], "discover")
        memory["date"] = date.today().isoformat()
        (self.repo / ".agents/skills/review").unlink()
        # Stage the deletion only, preserving the gitlink in the index.
        git(self.repo, "add", "-u", "--", ".agents")
        git(self.repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", "Remove reviewer")
        refreshed = assets.integrate(self.resolver(), memory)
        self.assertEqual(refreshed["action"], "discover")
        self.assertFalse(any("skills/" in r["path"] for r in refreshed["assets"]))

    def test_missing_object_stale_sibling_and_no_host(self):
        self.set_pin("1" * 40)
        before = git(self.repo, "status", "--porcelain")
        result = assets.integrate(self.resolver(), None, memory_available=False)
        self.assertIsNone(result["entry"])
        self.assertIn("unavailable", result["memory"])
        row = next(r for r in result["assets"] if r["path"] == "rules/tests.md")
        self.assertEqual(row["pin"], "1" * 40)
        self.assertIn("differs", row["warning"])
        self.assertEqual(row["revision"], git(self.rules, "rev-parse", "HEAD"))
        self.assertFalse(self.host_entry.exists())
        self.assertEqual(before, git(self.repo, "status", "--porcelain"))
        self.rules.rename(self.rules.with_name("unrelated"))
        failed = assets.integrate(self.resolver(), None)
        self.assertTrue(any("unresolved submodule" in r.get("error", "") for r in failed["assets"]))

    def test_heading_fallback_and_code_fences(self):
        self.assertEqual(assets.rule_labels("## Check timeouts\n~~~\n- **NO-2**\n~~~"), ["Check timeouts"])

    def test_new_rule_triggers_refresh_but_an_unrelated_blob_reuses_memory(self):
        memory = assets.integrate(self.resolver(), None)["entry"]
        for path, expected in (("data.txt", "reuse"), ("rules/new.md", "discover")):
            (self.repo / path).write_text("# New input\n")
            git(self.repo, "add", "--", path)
            git(self.repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                "-c", "commit.gpgsign=false", "commit", "-qm", "Add input")
            result = assets.integrate(self.resolver(), memory)
            self.assertEqual(result["action"], expected)
        self.assertIn("rules/new.md", result["rule_inventory"])

    def test_symlink_blob_to_initialized_module_then_retained_objects(self):
        target = "../handbook/review/SKILL.md"
        oid = subprocess.run(["git", "-C", str(self.repo), "hash-object", "-w", "--stdin"],
                             input=target, capture_output=True, check=True, text=True).stdout.strip()
        git(self.repo, "update-index", "--add", "--cacheinfo", f"120000,{oid},rules/link.md")
        git(self.repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", "Link the review checklist")
        checkout = self.repo / "handbook"
        git(self.repo, "clone", "-q", "--no-local", str(self.rules), str(checkout))
        row, text = self.resolver().resolve("rules/link.md")
        self.assertEqual((row["method"], row["revision"]), ("initialized submodule", self.pin))
        self.assertIn("QA-2", text)
        modules = self.repo / ".git/modules"
        modules.mkdir()
        (checkout / ".git").rename(modules / "guide")
        self.rules.rename(self.rules.with_name("offline"))
        row, _ = self.resolver().resolve("rules/link.md")
        self.assertEqual((row["method"], row["revision"]), ("submodule objects", self.pin))


if __name__ == "__main__":
    unittest.main()
