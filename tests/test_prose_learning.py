"""Exercise prose identity and consent gates, not prose quality or AI detection."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "agent-plugins/skills/review-retrospective/scripts/review_learning.py"
SPEC = importlib.util.spec_from_file_location("prose_learning", SCRIPT)
learning = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(learning)
NOW = "2026-11-09T12:00:00+01:00"
TEXT_HASH = "a" * 64
OTHER_HASH = "b" * 64


def prose_pair():
    common = {"task_id": "draft-1", "input_revision": "copy-2", "input_artifact": "copy.md",
              "report_artifact": "report.md", "model": "model-A"}
    edit = {**common, "run_id": "edit-1", "skill": "humanizer", "mode": "local-edit",
            "prose": {"language": "ru", "genre": "reply", "brief_artifact": "brief.md",
                      "voice_revision": "voice-v3", "input_text_sha256": OTHER_HASH,
                      "output_text_sha256": TEXT_HASH},
            "paired": {"skill": "ai-detector", "invoked": True, "run_id": "check-1",
                       "invocation_evidence": "task.md#check"}}
    detector = {**common, "run_id": "check-1", "skill": "ai-detector", "mode": "local",
                "prose": {"text_sha256": TEXT_HASH, "decisions_artifact": "decisions.md"},
                "paired": {"skill": "humanizer", "invoked": True, "run_id": "edit-1",
                           "invocation_evidence": "task.md#edit"}}
    return edit, detector


class ProseLearningTests(unittest.TestCase):
    def prepare(self, runs):
        return learning.prepare({"schema_version": 1, "runs": runs}, "draft-1")

    def pair_status(self, result, run_id="edit-1"):
        return next(c["status"] for c in result["prose_checks"] if c["run_id"] == run_id and c["kind"] == "pair")

    def external_status(self, detector):
        result = self.prepare([detector])
        return next(c["status"] for c in result["prose_checks"] if c["kind"] == "external-submission")

    def test_completed_pair_retains_voice_version_identity_and_invocation_sources(self):
        edit, detector = prose_pair()
        result = self.prepare([edit, detector])
        self.assertEqual(self.pair_status(result), "eligible")
        self.assertEqual(self.pair_status(result, "check-1"), "eligible")
        self.assertEqual(result["runs"][0]["prose"], edit["prose"])
        self.assertEqual(result["runs"][0]["paired"], edit["paired"])
        result["runs"][0]["prose"]["voice_revision"] = "changed"
        self.assertEqual(edit["prose"]["voice_revision"], "voice-v3")
        self.assertEqual(result["upstream_checks"], [])

    def test_absent_pair_is_skipped_without_requiring_another_skill(self):
        edit, detector = prose_pair()
        edit.pop("paired")
        self.assertEqual(self.pair_status(self.prepare([edit])), "skipped-invocation-unknown")
        edit["paired"] = {"skill": "ai-detector", "invoked": False, "run_id": "absent"}
        self.assertEqual(self.pair_status(self.prepare([edit])), "skipped-not-invoked")
        detector.pop("paired")
        self.assertEqual(self.external_status(detector), "skipped-local")

    def test_wrong_task_unavailable_artifact_and_wrong_copy_are_not_comparable(self):
        edit, detector = prose_pair()
        detector["task_id"] = "different-draft"
        self.assertEqual(self.pair_status(self.prepare([edit, detector])), "scope-mismatch")
        detector["task_id"] = "draft-1"
        detector["report_artifact"] = "unknown"
        self.assertEqual(self.pair_status(self.prepare([edit, detector])), "unavailable")
        detector["report_artifact"] = "check.md"
        detector["prose"]["text_sha256"] = OTHER_HASH
        self.assertEqual(self.pair_status(self.prepare([edit, detector])), "text-version-mismatch")
        detector["prose"].pop("text_sha256")
        self.assertEqual(self.pair_status(self.prepare([edit, detector])), "text-identity-unavailable")

    def test_external_feedback_requires_valid_submission_provenance_and_same_copy(self):
        _, detector = prose_pair()
        detector["mode"] = "external"
        detector["prose"]["external"] = external = {
            "submission_state": "valid", "submitted_text_sha256": TEXT_HASH,
            "provider": "fixture provider", "captured_at": NOW, "result_artifact": "result.md"}
        self.assertEqual(self.external_status(detector), "eligible")
        external["submitted_text_sha256"] = OTHER_HASH
        self.assertEqual(self.external_status(detector), "text-version-mismatch")
        external["submitted_text_sha256"] = None
        self.assertEqual(self.external_status(detector), "text-identity-unavailable")
        external["result_artifact"] = None
        self.assertEqual(self.external_status(detector), "provenance-unavailable")
        external["submission_state"] = "invalid"
        self.assertEqual(self.external_status(detector), "invalid")
        external["submission_state"] = "incomplete"
        self.assertEqual(self.external_status(detector), "incomplete")

    def test_pair_requires_both_runs_sources_in_either_direction(self):
        for index in (0, 1):
            for key in ("input_artifact", "report_artifact", "input_revision"):
                for missing in (None, "unknown", "   ", 3):
                    runs = list(prose_pair())
                    runs[index][key] = missing
                    with self.subTest(index=index, key=key, missing=missing):
                        result = self.prepare(runs)
                        self.assertEqual(self.pair_status(result, "edit-1"), "unavailable")
                        self.assertEqual(self.pair_status(result, "check-1"), "unavailable")

    def test_external_provenance_requires_a_dated_identifiable_source(self):
        _, detector = prose_pair()
        detector["mode"] = "external"
        valid = {"submission_state": "valid", "submitted_text_sha256": TEXT_HASH,
                 "provider": "fixture provider", "captured_at": NOW, "result_artifact": "result.md"}
        for key, invalid_values in (
                ("captured_at", ("not-a-time", "2026-11-09T12:00:00", "2026-11-09", "unknown")),
                ("provider", (None, "unknown", " ")),
                ("result_artifact", (None, "unknown", " "))):
            for invalid in invalid_values:
                detector["prose"]["external"] = {**valid, key: invalid}
                with self.subTest(key=key, invalid=invalid):
                    self.assertEqual(self.external_status(detector), "provenance-unavailable")
        for captured in (NOW, "2026-11-09T11:00:00Z"):
            detector["prose"]["external"] = {**valid, "captured_at": captured}
            self.assertEqual(self.external_status(detector), "eligible")

    def test_hashes_are_exact_and_malformed_identity_is_rejected(self):
        for value in ("A" * 64, "a" * 63, "not-a-hash", 4):
            edit, _ = prose_pair()
            edit["prose"]["output_text_sha256"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.prepare([edit])

    def test_new_semantic_feedback_is_selected_but_unchanged_evidence_is_not_relearned(self):
        edit, _ = prose_pair()
        event = {"event_id": "modality", "kind": "meaning-drift", "status": "verified", "priority": "P1",
                 "evidence": "before-after.md#must", "evidence_revision": "v2", "assessed_revision": "v1"}
        edit["feedback"] = [event]
        self.assertEqual(self.prepare([edit])["cases"][0]["kind"], "meaning-drift")
        event["assessed_revision"] = "v2"
        self.assertEqual(self.prepare([edit])["cases"], [])

    def test_prose_model_defaults_and_never_choice_remain_scoped_and_non_mutating(self):
        for skill in ("humanizer", "ai-detector"):
            data = {"policy": {"schema_version": 1, "defaults": {}, "decisions": {}},
                    "proposal": {"skill": skill, "stage": "local-pass", "risk_scope": "short-reply",
                                 "from_model": "model-A", "to_model": "model-B", "to_reasoning": "low"}}
            original = deepcopy(data)
            policy = learning.decide(data, "accept", NOW)
            self.assertEqual(next(iter(policy["defaults"].values()))["skill"], skill)
            self.assertEqual(data, original)
            data["policy"] = learning.decide(data, "never", NOW)
            self.assertFalse(learning.offer(data, "2027-01-01T00:00:00Z")["eligible"])
            data["proposal"]["stage"] = "different-stage"
            self.assertTrue(learning.offer(data, NOW)["eligible"])


if __name__ == "__main__":
    unittest.main()
