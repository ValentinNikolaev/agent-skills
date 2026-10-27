"""Verify review fixtures and their observable defects and clean controls.

These tests establish fixture behavior, not model review accuracy. Static
measurement cases supply evaluation inputs without claiming measured speedups.
"""

import json
from pathlib import Path
import subprocess
import sys
import unittest


FIXTURES = Path(__file__).parent / "fixtures" / "review_failure_controls.json"


class ReviewFailureControlTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads(FIXTURES.read_text(encoding="utf-8"))

    def test_runtime_pairs_have_discriminating_behavior(self):
        for topic in ("recoverable-exit", "callback-lock"):
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
