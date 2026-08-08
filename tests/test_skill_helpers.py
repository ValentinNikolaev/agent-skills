from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "agent-plugins" / "skills"


def run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )


class DeterministicHelperTests(unittest.TestCase):
    def test_assessment_validator_checks_verdicts_and_financial_formulas(self) -> None:
        helper = (
            SKILLS_ROOT
            / "business-viability-assessment"
            / "scripts"
            / "validate_assessment.py"
        )
        result = run([sys.executable, str(helper), "--self-test"], cwd=REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("invalid verdict and derived revenue rejected", result.stdout)

    def test_docs_checker_finds_real_links_and_ignores_example_paths(self) -> None:
        helper = SKILLS_ROOT / "audit-docs" / "scripts" / "check_docs.py"
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            docs = repo / "docs"
            docs.mkdir()
            (repo / "src").mkdir()
            (repo / "src" / "live.py").write_text("print('ok')\n", encoding="utf-8")
            (docs / "target.md").write_text("# Valid Target\n", encoding="utf-8")
            (docs / "index.md").write_text(
                "# Index\n\n"
                "[Good](target.md#valid-target)\n\n"
                "[Broken](missing.md)\n\n"
                "`examples/missing.py`\n\n"
                "```text\nexamples/also-missing.py\n```\n\n"
                "Historical location: legacy/removed.md\n\n"
                "Live path: src/live.py\n",
                encoding="utf-8",
            )

            result = run(
                [
                    sys.executable,
                    str(helper),
                    "--repo-root",
                    str(repo),
                    "docs",
                    "--format",
                    "json",
                    "--fail-on",
                    "never",
                ],
                cwd=repo,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            findings = json.loads(result.stdout)["findings"]
            codes = [item["code"] for item in findings]
            self.assertEqual(codes.count("BROKEN_LINK"), 1)
            self.assertNotIn("MISSING_PLAIN_PATH", codes)

    def test_review_scope_unions_staged_unstaged_and_untracked_files(self) -> None:
        helper = SKILLS_ROOT / "code-review" / "scripts" / "collect_review_scope.py"
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            commands = (
                ["git", "init"],
                ["git", "config", "user.name", "Fixture"],
                ["git", "config", "user.email", "fixture@example.invalid"],
                ["git", "config", "commit.gpgsign", "false"],
            )
            for command in commands:
                result = run(command, cwd=repo)
                self.assertEqual(result.returncode, 0, result.stderr)

            (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
            self.assertEqual(run(["git", "add", "tracked.txt"], cwd=repo).returncode, 0)
            commit = run(["git", "commit", "-m", "fixture"], cwd=repo)
            self.assertEqual(commit.returncode, 0, commit.stderr)

            (repo / "tracked.txt").write_text("base\nunstaged\n", encoding="utf-8")
            (repo / "staged.txt").write_text("staged\n", encoding="utf-8")
            self.assertEqual(run(["git", "add", "staged.txt"], cwd=repo).returncode, 0)
            (repo / "untracked.txt").write_text("untracked\n", encoding="utf-8")

            result = run(
                [sys.executable, str(helper), "--repo", str(repo), "--base", "HEAD"],
                cwd=REPO_ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["change_sources"]["staged"])
            self.assertTrue(payload["change_sources"]["unstaged"])
            self.assertTrue(payload["change_sources"]["untracked"])
            self.assertEqual(
                {item["path"] for item in payload["files"]},
                {"staged.txt", "tracked.txt", "untracked.txt"},
            )

    def test_pr_reader_offline_self_test_proves_fixed_read_only_queries(self) -> None:
        helper = SKILLS_ROOT / "fix-pr" / "scripts" / "read_pr_review.py"
        result = run(
            [sys.executable, str(helper), "--self-test"],
            cwd=REPO_ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["mutation_paths"], 0)
        self.assertGreaterEqual(payload["pagination_pages_tested"], 2)

    def test_memory_validator_accepts_contract_and_rejects_index_drift(self) -> None:
        helper = (
            REPO_ROOT
            / "agent-plugins"
            / "shared"
            / "memory"
            / "validate_memory.py"
        )
        with tempfile.TemporaryDirectory() as temporary:
            memory_root = Path(temporary)
            memory_file = memory_root / "architecture.md"
            memory_file.write_text(
                "---\n"
                "memory_contract: 1\n"
                "name: architecture\n"
                "description: Locate the project's durable architecture decisions.\n"
                "type: project\n"
                "related: []\n"
                "provenance:\n"
                "  - kind: repository\n"
                "    locator: .\n"
                "    retrieved_at: 2026-08-08\n"
                "    revision: fixture\n"
                "last_updated: 2026-08-08\n"
                "last_reviewed: 2026-08-08\n"
                "---\n\n"
                "# Architecture\n\nThe fixture has one durable fact.\n",
                encoding="utf-8",
            )
            index = memory_root / "MEMORY.md"
            index.write_text(
                "# Memory\n\n"
                "- [architecture.md](architecture.md) — project — Durable architecture decisions\n",
                encoding="utf-8",
            )

            valid = run(
                [
                    sys.executable,
                    str(helper),
                    str(memory_root),
                    "--today",
                    "2026-08-08",
                    "--format",
                    "json",
                ],
                cwd=REPO_ROOT,
            )
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertEqual(json.loads(valid.stdout)["status"], "pass")

            index.write_text("# Memory\n", encoding="utf-8")
            invalid = run(
                [
                    sys.executable,
                    str(helper),
                    str(memory_root),
                    "--today",
                    "2026-08-08",
                    "--format",
                    "json",
                ],
                cwd=REPO_ROOT,
            )
            self.assertEqual(invalid.returncode, 1)
            codes = {item["code"] for item in json.loads(invalid.stdout)["findings"]}
            self.assertIn("ORPHAN_MEMORY", codes)


if __name__ == "__main__":
    unittest.main()
