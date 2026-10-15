"""Keep the raw review examples executable and their controls discriminating.

These checks validate evaluation inputs, not model routing or review quality.
Only the repository-owned Python examples run, in isolated subprocesses.
"""

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "tests" / "fixtures" / "language_review_examples.json"


class LanguageReviewExampleTests(unittest.TestCase):
    def setUp(self):
        self.examples = json.loads(EXAMPLES.read_text(encoding="utf-8"))

    def test_each_language_has_a_defect_and_a_clean_control(self):
        for language in {case["language"] for case in self.examples}:
            cases = [case for case in self.examples if case["language"] == language]
            with self.subTest(language=language):
                self.assertTrue(any(case["expected_findings"] for case in cases))
                self.assertTrue(any(not case["expected_findings"] for case in cases))
        ids = [case["id"] for case in self.examples]
        self.assertEqual(len(ids), len(set(ids)))
        for case in self.examples:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["context"])
                if case["expected_findings"]:
                    self.assertIn(
                        case["location_line"], range(1, len(case["source"].splitlines()) + 1)
                    )
                else:
                    self.assertIsNone(case["location_line"])

    def test_python_examples_exhibit_the_recorded_behavior(self):
        for case in self.examples:
            if case["language"] != "python":
                continue
            with self.subTest(case=case["id"]):
                result = subprocess.run(
                    [sys.executable, "-I", "-c", case["source"] + "\n" + case["probe"]],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, case["observed_stdout"])


if __name__ == "__main__":
    unittest.main()
