"""Verify review fixtures and their observable defects and clean controls.

These tests establish fixture behavior, not model review accuracy. Static
measurement cases supply evaluation inputs without claiming measured speedups.
"""

import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest


FIXTURES = Path(__file__).parent / "fixtures" / "review_failure_controls.json"
DELTAS = FIXTURES.parent / "code_review_deltas"


def delta_versions(case):
    """Run the repository-owned one-file fixture before and after its review patch."""
    source = DELTAS / "base" / case["source_file"]
    patch = (DELTAS / case["patch"]).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / source.name
        target.write_bytes(source.read_text(encoding="utf-8").encode())
        before = runpy.run_path(str(target))
        subprocess.run(["git", "apply", "--no-index", "-"], cwd=tmp,
                       input=patch.encode(), capture_output=True, check=True)
        return before, runpy.run_path(str(target))


class ReviewFailureControlTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(FIXTURES.read_text(encoding="utf-8"))

    def test_permission_check_deltas(self):
        cases = {c["id"]: c for c in self.cases if c["topic"] == "permission-check-phase"}
        self.assertEqual(set(cases), {"K7", "R2"})
        self.assertEqual(cases["K7"]["context_file"], cases["R2"]["context_file"])
        self.assertTrue((DELTAS / cases["K7"]["context_file"]).is_file())
        cached = {"selected": "record", "other": "unrelated"}
        closed = (None, {"other": "unrelated"}, "closed")
        expected = {
            ("open", 200): ("record", cached, "watch"),
            ("open", 403): (None, cached, "fresh"),
            ("open", 503): (None, cached, "retry"),
            ("watch", 200): ("record", cached, "watch"),
            ("watch", 403): closed,
            ("watch", 503): ("record", cached, "retry"),
        }
        for case_id, case in cases.items():
            self.assertEqual(len(case["expected_findings"]), int(case_id == "K7"))
            for revision, module in zip(("base", "head"), delta_versions(case)):
                outcomes = expected.copy()
                if revision == "base":
                    outcomes["open", 403] = closed
                elif case_id == "K7":
                    outcomes["watch", 403] = ("record", cached, "fresh")
                for (phase, status), wanted in outcomes.items():
                    with self.subTest(case=case_id, revision=revision, phase=phase, status=status):
                        panel = module["Panel"](cache=cached.copy())
                        if phase == "open":
                            panel.open_result("selected", status)
                        else:
                            panel.open_result("selected", 200)
                            panel.watch_result("selected", status)
                        self.assertEqual((panel.visible, panel.cache, panel.action), wanted)

    def test_partial_batch_delta(self):
        case = next(c for c in self.cases if c["id"] == "M4")
        self.assertTrue((DELTAS / case["context_file"]).is_file())
        self.assertEqual(len(case["expected_findings"]), 1)
        before, after = delta_versions(case)
        for items, old, new in [(0, 1, 0), (1, 1, 0), (4, 1, 1), (5, 2, 1)]:
            with self.subTest(items=items):
                self.assertEqual(before["batch_count"](items, 4), old)
                self.assertEqual(after["batch_count"](items, 4), new)

    def test_runtime_pairs_have_discriminating_behavior(self):
        for topic in ("recoverable-exit", "callback-lock", "remote-call-budget"):
            pair = [case for case in self.cases if case["topic"] == topic]
            with self.subTest(topic=topic):
                self.assertEqual(len(pair), 2)
                self.assertEqual(pair[0]["context"], pair[1]["context"])
                self.assertEqual(sum(bool(case["expected_findings"]) for case in pair), 1)
                self.assertNotEqual(
                    (pair[0]["returncode"], pair[0]["stdout"]),
                    (pair[1]["returncode"], pair[1]["stdout"]),
                )

    def test_runtime_examples_exhibit_recorded_outcomes(self):
        for case in self.cases:
            if case["verification"] != "runtime":
                continue
            with self.subTest(case=case["id"]):
                result = subprocess.run(
                    [sys.executable, "-I", "-c", case["source"]],
                    capture_output=True, text=True, timeout=5, check=False,
                )
                self.assertEqual(result.returncode, case["returncode"], result.stderr)
                self.assertEqual(result.stdout, case["stdout"])

    def test_clean_controls_include_intentional_fail_stop_and_reentrant_lock(self):
        for case_id in ("internal-invariant-fail-stop", "callback-reentrant-lock"):
            case = next(case for case in self.cases if case["id"] == case_id)
            with self.subTest(case=case_id):
                self.assertEqual(case["expected_findings"], [])
                self.assertEqual(case["verification"], "runtime")

    def test_measurement_cases_separate_missing_evidence_from_defects(self):
        cases = {case["id"]: case for case in self.cases if case["topic"] == "measurements"}
        self.assertEqual(len(cases), 3)
        for case in cases.values():
            self.assertEqual(case["expected_findings"], [])
            self.assertEqual(case["verification"], "static")
        comparable = cases["comparable-measurements"]
        mismatched = cases["incomparable-measurements"]
        absent = cases["missing-measurements"]
        self.assertEqual(comparable["baseline"]["requests"], comparable["candidate"]["requests"])
        self.assertNotEqual(mismatched["baseline"]["requests"], mismatched["candidate"]["requests"])
        self.assertIsNone(absent["candidate"])
        self.assertFalse(comparable["expected_verification_limits"])
        self.assertTrue(mismatched["expected_verification_limits"])
        self.assertTrue(absent["expected_verification_limits"])


if __name__ == "__main__":
    unittest.main()
