from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import skill_health as health  # noqa: E402

TODAY = date(2026, 11, 9)
LONG_SENTENCE = (
    "Reuse existing evidence and verify only the claims that are stale, "
    "contradictory, or unsupported before relying on them."
)


def write_skill(
    root: Path,
    name: str,
    body: str = "# Skill\n\nDo the work.\n",
    *,
    description: str | None = None,
    references: dict[str, str] | None = None,
    yaml_extra: str = "",
) -> Path:
    directory = root / "agent-plugins" / "skills" / name
    directory.mkdir(parents=True, exist_ok=True)
    description = description or f"Fixture skill {name} for health tests."
    (directory / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n{body}",
        encoding="utf-8",
    )
    agents = directory / "agents"
    agents.mkdir(exist_ok=True)
    (agents / "openai.yaml").write_text(
        "interface:\n"
        f'  display_name: "{name}"\n'
        f'  short_description: "Short text for {name} skill"\n'
        f'  default_prompt: "Use ${name} now."\n' + yaml_extra,
        encoding="utf-8",
    )
    for relative, text in (references or {}).items():
        target = directory / "references" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return directory


def write_manifests(root: Path, version: str = "30.0.0") -> None:
    for platform in ("claude", "codex"):
        directory = root / f".{platform}-plugin"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "plugin.json").write_text(
            json.dumps({"name": "fixture", "version": version}) + "\n",
            encoding="utf-8",
        )


def tree_digest(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and ".git" not in path.parts
    }


def run_cli(root: Path, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = health.run(["--repo-root", str(root), *argv])
    return code, out.getvalue(), err.getvalue()


def metrics_for(root: Path, **settings: object) -> dict:
    merged = {**health.DEFAULT_SETTINGS, **settings}
    return health.compute_metrics(root, merged, TODAY)


def findings_for(
    root: Path,
    baseline: dict | None = None,
    next_major: int | None = 30,
    **settings: object,
) -> list[dict]:
    merged = {**health.DEFAULT_SETTINGS, **settings}
    metrics = health.compute_metrics(root, merged, TODAY)
    return health.evaluate(metrics, merged, baseline, next_major)


def by_metric(found: list[dict], metric: str) -> list[dict]:
    return [item for item in found if item["metric"] == metric]


class DueDecisionTests(unittest.TestCase):
    def test_no_baseline_is_due(self) -> None:
        due, reason = health.decide_due(30, None, 3)
        self.assertTrue(due)
        self.assertIn("no healthcheck baseline", reason)

    def test_interval_counts_majors_from_the_recorded_major(self) -> None:
        cases = {
            (30, 30): False,
            (32, 30): False,
            (33, 30): True,
            (34, 30): True,
            # A late check moves the next one: 33 is not due after recording 31.
            (33, 31): False,
            (34, 31): True,
        }
        for (next_major, last), expected in cases.items():
            with self.subTest(next_major=next_major, last=last):
                self.assertEqual(health.decide_due(next_major, last, 3)[0], expected)

    def test_interval_is_configurable(self) -> None:
        self.assertFalse(health.decide_due(33, 30, 4)[0])
        self.assertTrue(health.decide_due(34, 30, 4)[0])

    def test_unknown_next_version_is_not_due_once_a_baseline_exists(self) -> None:
        self.assertFalse(health.decide_due(None, 30, 3)[0])


class LedgerTests(unittest.TestCase):
    def test_missing_ledger_uses_defaults_without_a_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            ledger = health.load_ledger(Path(temporary) / "missing.json")
        self.assertEqual(ledger["settings"]["interval_majors"], 3)
        self.assertIsNone(ledger["last_check"])
        self.assertIsNone(ledger["baseline"])

    def test_partial_settings_merge_with_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "ledger.json"
            path.write_text(json.dumps({"schema": 1, "settings": {"interval_majors": 5}}))
            ledger = health.load_ledger(path)
        self.assertEqual(ledger["settings"]["interval_majors"], 5)
        self.assertEqual(ledger["settings"]["description_max_chars"], 250)

    def test_invalid_ledgers_are_rejected(self) -> None:
        bad = {
            "not json": "{",
            "not an object": "[]",
            "unknown schema": json.dumps({"schema": 9}),
            "zero interval": json.dumps({"settings": {"interval_majors": 0}}),
            "string interval": json.dumps({"settings": {"interval_majors": "3"}}),
        }
        for label, text in bad.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "ledger.json"
                path.write_text(text)
                with self.assertRaises(health.HealthError):
                    health.load_ledger(path)

    def test_committed_ledger_is_valid_and_unrecorded_or_consistent(self) -> None:
        ledger = health.load_ledger(REPO_ROOT / health.DEFAULT_LEDGER)
        last = ledger["last_check"]
        self.assertEqual(ledger["settings"]["interval_majors"], 3)
        if last is not None:
            self.assertEqual(last["major"], health.version_tuple(last["version"])[0])
            self.assertIn(last["kind"], health.CHECK_KINDS)
            self.assertIsNotNone(ledger["baseline"])


class MetricTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.addCleanup(self._temporary.cleanup)

    def test_body_ceiling_and_growth(self) -> None:
        write_skill(self.root, "alpha", "# A\n\n" + "word " * 60)
        write_skill(self.root, "beta", "# B\n\n" + "word " * 20)
        found = findings_for(self.root, body_word_ceiling=50)
        self.assertEqual([i["skill"] for i in by_metric(found, "body-size")], ["alpha"])
        self.assertEqual(by_metric(found, "body-size")[0]["severity"], "error")

        baseline = {"skills": {"beta": {"body_words": 5}, "alpha": {"body_words": 60}}}
        found = findings_for(self.root, baseline=baseline, body_growth_words=10)
        self.assertEqual([i["skill"] for i in by_metric(found, "body-growth")], ["beta"])
        self.assertEqual(by_metric(found, "body-growth")[0]["severity"], "warn")

    def test_ceiling_defaults_to_the_validators_constant(self) -> None:
        import validate_skills

        write_skill(self.root, "alpha", "# A\n\n" + "word " * 10)
        with mock.patch.object(validate_skills, "MAX_SKILL_BODY_WORDS", 5):
            found = findings_for(self.root)
        self.assertEqual(len(by_metric(found, "body-size")), 1)

    def test_routing_budget_and_description_length(self) -> None:
        write_skill(self.root, "alpha", description="x" * 300)
        metrics = metrics_for(self.root)
        found = health.evaluate(metrics, health.DEFAULT_SETTINGS, None, 30)
        self.assertEqual(len(by_metric(found, "description-length")), 1)
        self.assertEqual(by_metric(found, "routing-budget"), [])
        metrics["routing_budget"] = 100
        found = health.evaluate(metrics, health.DEFAULT_SETTINGS, None, 30)
        self.assertEqual(by_metric(found, "routing-budget")[0]["severity"], "error")

    def test_shared_sentences_are_flagged_once_and_only_when_new(self) -> None:
        write_skill(self.root, "alpha", f"# A\n\n{LONG_SENTENCE}\n")
        write_skill(self.root, "beta", f"# B\n\n{LONG_SENTENCE}\n\nShort shared line.\n")
        write_skill(self.root, "gamma", "# C\n\nShort shared line.\n")
        found = findings_for(self.root)
        shared = by_metric(found, "shared-sentence")
        self.assertEqual(len(shared), 1)
        self.assertIn("alpha, beta", shared[0]["message"])
        self.assertEqual(shared[0]["severity"], "info")

        metrics = metrics_for(self.root)
        baseline = health.baseline_from_metrics(metrics)
        self.assertEqual(
            by_metric(findings_for(self.root, baseline=baseline), "shared-sentence"), []
        )
        write_skill(
            self.root,
            "delta",
            "# D\n\nA second long sentence that two skills now repeat word for word here.\n",
        )
        write_skill(
            self.root,
            "epsilon",
            "# E\n\nA second long sentence that two skills now repeat word for word here.\n",
        )
        fresh = by_metric(findings_for(self.root, baseline=baseline), "shared-sentence")
        self.assertEqual(len(fresh), 1)
        self.assertEqual(fresh[0]["severity"], "warn")
        self.assertIn("delta, epsilon", fresh[0]["message"])

    def test_allowlisted_files_and_licences_do_not_count_as_shared(self) -> None:
        write_skill(self.root, "alpha", references={"memory-contract.md": LONG_SENTENCE + "\n"})
        write_skill(self.root, "beta", references={"memory-contract.md": LONG_SENTENCE + "\n"})
        self.assertEqual(by_metric(findings_for(self.root), "shared-sentence"), [])
        self.assertEqual(by_metric(findings_for(self.root), "near-duplicate"), [])

    def test_orphan_references(self) -> None:
        write_skill(
            self.root,
            "alpha",
            "# A\n\nSee [linked](references/linked.md) and `references/named.md`.\n",
            references={
                "linked.md": "# Linked\n\nSee [chained](chained.md).\n",
                "chained.md": "# Chained\n",
                "named.md": "# Named\n",
                "orphan.md": "# Orphan\n",
                "data.json": "{}",
            },
        )
        found = by_metric(findings_for(self.root), "orphan-reference")
        self.assertEqual(
            sorted(item["location"] for item in found),
            ["references/data.json", "references/orphan.md"],
        )

    def test_bare_script_paths(self) -> None:
        write_skill(
            self.root,
            "alpha",
            '# A\n\nRun `python scripts/run.py` or python3 scripts/x.py.\n\n'
            'Good: python "<skill-dir>/scripts/run.py".\n'
            "Also fine: `python -m unittest discover -s tests`.\n",
        )
        write_skill(self.root, "wrap-agent-skill", "# W\n\npython scripts/validate_skills.py\n")
        found = by_metric(findings_for(self.root), "bare-script-path")
        self.assertEqual({item["skill"] for item in found}, {"alpha"})
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["location"], "SKILL.md:8")

    def test_version_milestones_trigger_at_or_below_the_next_major(self) -> None:
        write_skill(
            self.root,
            "alpha",
            "# A\n\nThis entry is planned for removal in v30.\n\n"
            "Keep it through v29.\n\nUse Zod v3 or Go v1 normally.\n",
        )
        self.assertEqual(len(by_metric(findings_for(self.root, next_major=29), "version-milestone")), 1)
        self.assertEqual(len(by_metric(findings_for(self.root, next_major=30), "version-milestone")), 2)
        self.assertEqual(by_metric(findings_for(self.root, next_major=28), "version-milestone"), [])
        self.assertEqual(by_metric(findings_for(self.root, next_major=None), "version-milestone"), [])

    def test_non_canonical_backticked_skill_names(self) -> None:
        write_skill(self.root, "alpha-review", "# A\n\nRoute edits to `beta-review`.\n")
        write_skill(
            self.root,
            "beta-review",
            "# B\n\nUse `alpha-review` for diffs, not `review-alpha`. Then `old-pages` is gone.\n"
            "Flag `--dry-run` and `some-file-name` freely. Use `stop-slop` never.\n",
        )
        found = by_metric(findings_for(self.root), "stale-skill-name")
        self.assertEqual(
            sorted(item["message"].split("`")[1] for item in found),
            ["review-alpha", "stop-slop"],
        )

    def test_stale_as_of_facts(self) -> None:
        write_skill(
            self.root,
            "alpha",
            "# A\n\nAs of 2026-01-01 the limit is 10.\n\n"
            "As of 2026-11-01 the limit is 20.\n\nChecked on March 2026 only.\n",
        )
        found = by_metric(findings_for(self.root), "stale-fact")
        self.assertEqual(len(found), 2)
        self.assertTrue(all(item["skill"] == "alpha" for item in found))

    def test_yaml_key_outliers_and_summary_drift(self) -> None:
        for number in range(12):
            write_skill(self.root, f"skill-{number}")
        write_skill(self.root, "special", yaml_extra="policy:\n  allow_implicit_invocation: true\n")
        found = by_metric(findings_for(self.root), "yaml-outlier")
        self.assertEqual(len(found), 1)
        self.assertIn("special", found[0]["message"])

        baseline = health.baseline_from_metrics(metrics_for(self.root))
        write_skill(self.root, "skill-1", description="A new description for skill one tests.")
        drift = by_metric(findings_for(self.root, baseline=baseline), "summary-drift")
        self.assertEqual([item["skill"] for item in drift], ["skill-1"])

    def test_near_duplicate_files_are_flagged(self) -> None:
        paragraph = " ".join(f"token{n}" for n in range(80))
        write_skill(self.root, "alpha", references={"a.md": paragraph})
        write_skill(self.root, "beta", references={"b.md": paragraph + " extra words"})
        found = by_metric(findings_for(self.root), "near-duplicate")
        self.assertEqual(len(found), 1)


class CommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.addCleanup(self._temporary.cleanup)
        write_skill(self.root, "alpha")
        write_skill(self.root, "beta")
        write_manifests(self.root, "30.0.0")

    def test_due_and_check_work_without_a_baseline_and_write_nothing(self) -> None:
        before = tree_digest(self.root)
        code, out, err = run_cli(self.root, "due")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("Last healthcheck:       none recorded", out)
        self.assertIn("DUE (no healthcheck baseline is recorded)", out)
        code, out, err = run_cli(self.root, "check")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("Baseline: none recorded", out)
        code, out, _err = run_cli(self.root, "check", "--format", "json")
        payload = json.loads(out)
        self.assertFalse(payload["baseline"])
        self.assertFalse(payload["delta"]["available"])
        self.assertEqual(tree_digest(self.root), before)

    def test_record_writes_only_the_ledger_and_then_due_follows_the_interval(self) -> None:
        skills_before = tree_digest(self.root)
        code, out, err = run_cli(
            self.root,
            "record",
            "--kind",
            "full-audit",
            "--reference",
            "audit at 66602cc",
            "--date",
            "2026-11-09",
            "--version",
            "30.0.0",
            "--commit",
            "abc123",
            "--open-item",
            "one open finding",
        )
        self.assertEqual((code, err), (0, ""), out)
        self.assertIn("falls due when a release would become v33", out)
        ledger_path = self.root / health.DEFAULT_LEDGER
        self.assertTrue(ledger_path.is_file())
        after = tree_digest(self.root)
        self.assertEqual(
            set(after) - set(skills_before), {health.DEFAULT_LEDGER.as_posix()}
        )
        self.assertEqual(
            {key: value for key, value in after.items() if key in skills_before},
            skills_before,
        )

        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(
            {key: ledger["last_check"][key] for key in ("version", "major", "commit", "date", "kind", "reference")},
            {
                "version": "30.0.0",
                "major": 30,
                "commit": "abc123",
                "date": "2026-11-09",
                "kind": "full-audit",
                "reference": "audit at 66602cc",
            },
        )
        self.assertEqual(ledger["open_items"], ["one open finding"])
        self.assertEqual(ledger["settings"]["interval_majors"], 3)
        self.assertEqual(sorted(ledger["baseline"]["skills"]), ["alpha", "beta"])

        state = health.due_state(self.root, health.load_ledger(ledger_path), project=False)
        self.assertEqual(state["next_major"], 30)
        self.assertFalse(state["due"])
        write_manifests(self.root, "32.4.0")
        state = health.due_state(self.root, health.load_ledger(ledger_path), project=False)
        self.assertFalse(state["due"])
        write_manifests(self.root, "33.0.0")
        state = health.due_state(self.root, health.load_ledger(ledger_path), project=False)
        self.assertTrue(state["due"])

    def test_record_keeps_settings_history_and_dry_run_writes_nothing(self) -> None:
        ledger_path = self.root / health.DEFAULT_LEDGER
        health.write_ledger(
            ledger_path,
            {**health.empty_ledger(), "settings": {**health.DEFAULT_SETTINGS, "interval_majors": 4}},
        )
        args = ["record", "--version", "30.0.0", "--commit", "c1", "--date", "2026-11-09"]
        before = ledger_path.read_bytes()
        code, out, _err = run_cli(self.root, *args, "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["last_check"]["commit"], "c1")
        self.assertEqual(ledger_path.read_bytes(), before)

        self.assertEqual(run_cli(self.root, *args)[0], 0)
        self.assertEqual(
            run_cli(self.root, "record", "--version", "34.0.0", "--commit", "c2", "--date", "2026-12-01")[0],
            0,
        )
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        self.assertEqual(ledger["settings"]["interval_majors"], 4)
        self.assertEqual(ledger["last_check"]["major"], 34)
        self.assertEqual([item["commit"] for item in ledger["history"]], ["c1"])

    def test_record_requires_a_version_when_none_can_be_found(self) -> None:
        shutil.rmtree(self.root / ".claude-plugin")
        shutil.rmtree(self.root / ".codex-plugin")
        code, _out, err = run_cli(self.root, "record", "--commit", "c1")
        self.assertEqual(code, 1)
        self.assertIn("pass --version", err)

    def test_check_strict_exits_nonzero_on_warnings(self) -> None:
        write_skill(self.root, "gamma", "# G\n\nRun `python scripts/run.py` now.\n")
        self.assertEqual(run_cli(self.root, "check")[0], 0)
        self.assertEqual(run_cli(self.root, "check", "--strict")[0], 1)

    def test_json_due_reports_the_projection_and_next_release(self) -> None:
        code, out, _err = run_cli(self.root, "due", "--format", "json")
        self.assertEqual(code, 0)
        state = json.loads(out)
        # Nothing is generated yet, so a real run would add files: a major bump.
        self.assertEqual(state["projected_bump"], "major")
        self.assertEqual(state["projected_version"], "31.0.0")
        self.assertEqual(state["next_release_version"], "31.0.0")
        self.assertTrue(state["due"])

    def test_invalid_dates_are_reported(self) -> None:
        code, _out, err = run_cli(self.root, "check", "--today", "yesterday")
        self.assertEqual(code, 1)
        self.assertIn("--today must be YYYY-MM-DD", err)


@unittest.skipUnless(shutil.which("git"), "git is required")
class GitTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> str:
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
            cwd=root,
            check=True,
            capture_output=True,
            encoding="utf-8",
        ).stdout

    def setUp(self) -> None:
        self._temporary = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary.name)
        self.addCleanup(self._temporary.cleanup)
        write_skill(self.root, "alpha", "# A\n\nHand off to `beta`.\n")
        write_skill(self.root, "beta")
        write_skill(self.root, "gamma")
        write_manifests(self.root, "30.0.0")
        self.git(self.root, "init", "-q")
        self.git(self.root, "add", "-A")
        self.git(self.root, "commit", "-q", "-m", "base")
        self.base = self.git(self.root, "rev-parse", "HEAD").strip()

    def test_versions_distinguish_committed_prepared_and_working_tree(self) -> None:
        state = health.due_state(self.root, health.empty_ledger(), project=False)
        self.assertEqual(state["committed_version"], "30.0.0")
        self.assertIsNone(state["prepared_version"])
        write_manifests(self.root, "31.0.0+codex.20261109000000")
        state = health.due_state(self.root, health.empty_ledger(), project=False)
        self.assertEqual(state["committed_version"], "30.0.0")
        self.assertEqual(state["working_tree_version"], "31.0.0")
        self.assertEqual(state["prepared_version"], "31.0.0")
        self.assertEqual(state["next_release_version"], "31.0.0")

    def test_delta_scope_lists_changed_skills_and_their_neighbours(self) -> None:
        alpha = self.root / "agent-plugins" / "skills" / "alpha" / "SKILL.md"
        alpha.write_text(alpha.read_text(encoding="utf-8") + "\nMore.\n", encoding="utf-8")
        write_skill(self.root, "delta")
        scope = health.delta_scope(
            self.root,
            self.base,
            {"alpha", "beta", "gamma", "delta"},
            {"alpha": "Hand off to `beta`.", "delta": ""},
        )
        self.assertTrue(scope["available"])
        self.assertEqual(scope["changed"], ["alpha", "delta"])
        self.assertEqual(scope["neighbours"], ["beta"])

    def test_delta_scope_is_unavailable_without_a_known_commit(self) -> None:
        self.assertFalse(health.delta_scope(self.root, None, set(), {})["available"])
        self.assertFalse(
            health.delta_scope(self.root, "0" * 40, set(), {})["available"]
        )

    def test_record_captures_head_and_dirty_state(self) -> None:
        self.assertEqual(run_cli(self.root, "record", "--version", "30.0.0")[0], 0)
        ledger = json.loads((self.root / health.DEFAULT_LEDGER).read_text(encoding="utf-8"))
        self.assertEqual(ledger["last_check"]["commit"], self.base)
        self.assertIn("dirty", ledger["last_check"])
        code, out, _err = run_cli(self.root, "check", "--format", "json")
        self.assertEqual(code, 0)
        delta = json.loads(out)["delta"]
        self.assertTrue(delta["available"])
        self.assertEqual(delta["changed"], [])


if __name__ == "__main__":
    unittest.main()
