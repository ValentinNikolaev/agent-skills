"""Exercise evidence selection, real accounting, and scoped reminder decisions.

These deterministic tests do not measure model review quality or savings.
"""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "agent-plugins/skills/review-retrospective/scripts/review_learning.py"
SPEC = importlib.util.spec_from_file_location("review_learning", SCRIPT)
learning = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(learning)
NOW = "2026-11-08T12:00:00+01:00"


def run_record(run_id="cr-1", skill="code-review", task="task-1"):
    return {"run_id": run_id, "task_id": task, "skill": skill,
            "input_revision": "before..after", "input_artifact": "input.md", "report_artifact": "report.md"}


def envelope():
    return {"policy": {"schema_version": 1, "defaults": {}, "decisions": {}, "local_note": "preserve"},
            "proposal": {"skill": "code-review", "stage": "scope", "risk_scope": "mechanical",
                         "from_model": "model-A", "to_model": "model-B", "to_reasoning": "low"}}


class ReviewLearningTests(unittest.TestCase):
    def prepare(self, runs, cap=5):
        return learning.prepare({"schema_version": 1, "runs": runs}, "task-1", cap)

    def test_upstream_requires_actual_invocation_same_task_and_available_artifacts(self):
        code, plan = run_record(), run_record("plan-1", "plan-review")
        code["upstream"] = [{"skill": "plan-review", "invoked": True, "run_id": "plan-1",
                             "invocation_evidence": "task-log#plan"},
                            {"skill": "review-arch", "invoked": False}]
        statuses = lambda: [item["status"] for item in self.prepare([code, plan])["upstream_checks"]]
        self.assertEqual(statuses(), ["eligible", "skipped-not-invoked"])
        plan["task_id"] = "other-task"
        self.assertEqual(statuses()[0], "scope-mismatch")
        plan["task_id"] = "task-1"
        plan["report_artifact"] = "unknown"
        self.assertEqual(statuses()[0], "unavailable")
        code.pop("upstream")
        self.assertEqual(statuses(), ["skipped-invocation-unknown"] * 2)

    def test_spec_review_is_a_recordable_run_and_an_optional_upstream_stage(self):
        spec_run = run_record("spec-1", "review-spec")
        self.assertEqual(self.prepare([spec_run])["runs"][0]["skill"], "review-spec")
        code = run_record()
        code["upstream"] = [{"skill": "review-spec", "invoked": True, "run_id": "spec-1",
                             "invocation_evidence": "task-log#spec"}]
        checks = self.prepare([code, spec_run])["upstream_checks"]
        self.assertEqual([(item["skill"], item["status"]) for item in checks],
                         [("plan-review", "skipped-invocation-unknown"),
                          ("review-arch", "skipped-invocation-unknown"),
                          ("review-spec", "eligible")])

    def test_known_invocation_without_run_is_unavailable_not_a_review_miss(self):
        code = run_record()
        code["upstream"] = [{"skill": "plan-review", "invoked": True, "run_id": "absent"}]
        self.assertEqual(self.prepare([code])["upstream_checks"][0]["status"], "unavailable")

    def test_new_evidence_is_sorted_capped_and_unchanged_assessments_are_skipped(self):
        code = run_record()
        event = {"event_id": "old", "kind": "missed-defect", "priority": "P1", "status": "verified",
                 "evidence": "result.md", "evidence_revision": "v1", "assessed_revision": "v1"}
        code["feedback"] = [event, {**event, "event_id": "new-low", "priority": "P3", "evidence_revision": "v2"},
                            {**event, "event_id": "new-high", "status": "disputed", "evidence_revision": "v2"}]
        original = deepcopy(code)
        result = self.prepare([code, run_record("other", task="other-task")], 1)
        self.assertEqual(result["cases"][0]["event_id"], "new-high")
        self.assertEqual(result["cases"][0]["status"], "disputed")
        self.assertEqual((result["already_assessed_count"], result["deferred_count"]), (1, 1))
        self.assertEqual(code, original)

    def test_tokens_are_not_double_counted_and_missing_values_stay_unknown(self):
        code = run_record()
        code["usage"] = {"input_tokens": 100, "output_tokens": 20, "cached_input_tokens": 80, "reasoning_tokens": 10}
        self.assertEqual(self.prepare([code])["runs"][0]["usage"]["total_tokens"], 120)
        code["usage"].pop("output_tokens")
        self.assertIsNone(self.prepare([code])["runs"][0]["usage"]["total_tokens"])
        self.assertIsNone(self.prepare([code])["runs"][0]["timing"]["elapsed_seconds"])

    def test_prepared_capsule_retains_scope_outcome_limits_stage_and_evidence_age(self):
        code = run_record()
        context = {"stage": "verification", "scope": ["worker.py"], "outcome": "COMMENT",
                   "coverage_limits": ["remote flags unavailable"], "captured_at": NOW}
        code.update(context)
        result = self.prepare([code])["runs"][0]
        self.assertEqual({key: result[key] for key in context}, context)
        result["coverage_limits"].clear()
        self.assertEqual(code["coverage_limits"], ["remote flags unavailable"])
        unknown = self.prepare([run_record()])["runs"][0]
        self.assertTrue(all(unknown[key] is None for key in context))

    def test_percent_windows_resets_and_shared_usage_prevent_false_attribution(self):
        code = run_record()
        snapshot = {"kind": "subscription", "window": "weekly", "source": "host status",
                    "before_window_id": "A", "after_window_id": "A",
                    "before_percent": 30, "after_percent": 32, "exclusive": False}
        code["limit_usage"] = [snapshot]
        limit = lambda: self.prepare([code])["runs"][0]["limit_usage"][0]
        self.assertEqual(limit()["observed_delta_pp"], 2)
        self.assertIsNone(limit()["review_delta_pp"])
        snapshot["exclusive"] = True
        self.assertEqual(limit()["review_delta_pp"], 2)
        snapshot["after_window_id"] = "B"
        self.assertIsNone(limit()["observed_delta_pp"])
        snapshot["after_window_id"], snapshot["after_percent"] = "A", 5
        self.assertIsNone(limit()["review_delta_pp"])

    def test_invalid_measurements_and_duplicate_ids_fail(self):
        for invalid in (-1, True, float("nan"), 1.5):
            code = run_record()
            code["usage"] = {"input_tokens": invalid}
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                self.prepare([code])
        with self.assertRaises(ValueError):
            self.prepare([run_record(), run_record()])
        code = run_record()
        code["timing"] = {"elapsed_seconds": 10, "waiting_seconds": 11}
        with self.assertRaises(ValueError):
            self.prepare([code])

    def test_accept_is_scoped_preserves_existing_policy_and_does_not_mutate_input(self):
        data = envelope()
        data["policy"]["defaults"]["existing"] = {"model": "keep"}
        original = deepcopy(data)
        policy = learning.decide(data, "accept", NOW)
        self.assertEqual(data, original)
        self.assertEqual(policy["local_note"], "preserve")
        self.assertEqual(policy["defaults"]["existing"], {"model": "keep"})
        chosen = [v for k, v in policy["defaults"].items() if k != "existing"][0]
        self.assertEqual((chosen["stage"], chosen["risk_scope"], chosen["model"]), ("scope", "mechanical", "model-B"))
        data["policy"] = policy
        self.assertFalse(learning.offer(data, NOW)["eligible"])

    def test_decline_without_reminder_answer_is_suppressed(self):
        data = envelope()
        data["policy"] = learning.decide(data, "decline", NOW)
        self.assertEqual(learning.offer(data, "2027-01-01T00:00:00Z")["reason"], "declined-pending")

    def test_week_reminder_is_not_early_and_is_consumed_once(self):
        data = envelope()
        data["policy"] = learning.decide(data, "remind-week", NOW)
        self.assertFalse(learning.offer(data, "2026-11-15T11:59:59+01:00")["eligible"])
        due = "2026-11-15T12:00:00+01:00"
        self.assertEqual(learning.offer(data, due)["reason"], "one-reminder-due")
        data["policy"] = learning.decide(data, "reminder-shown", due)
        self.assertFalse(learning.offer(data, "2026-11-22T12:00:00+01:00")["eligible"])
        with self.assertRaises(ValueError):
            learning.decide(data, "reminder-shown", due)

    def test_never_survives_new_evidence_and_does_not_suppress_other_stages(self):
        data = envelope()
        data["policy"] = learning.decide(data, "never", NOW)
        data["proposal"]["evidence"] = ["new-comparison.md"]
        self.assertFalse(learning.offer(data, "2027-01-01T00:00:00Z")["eligible"])
        data["proposal"]["stage"] = "verification"
        self.assertTrue(learning.offer(data, NOW)["eligible"])

    def test_cli_reads_stdin_emits_json_and_rejects_bad_input_without_report(self):
        command = [sys.executable, str(SCRIPT), "prepare", "--input", "-", "--task", "task-1"]
        result = subprocess.run(command, input=json.dumps({"schema_version": 1, "runs": [run_record()]}),
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["cases"], [])
        invalid = subprocess.run(command, input="{}", text=True, capture_output=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(invalid.stdout, "")


if __name__ == "__main__":
    unittest.main()
