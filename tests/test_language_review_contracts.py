"""Keep the raw review examples executable and their controls discriminating.

These checks validate evaluation inputs, not model routing or review quality.
Only repository-owned examples run, in isolated subprocesses. Optional Node
execution strips TypeScript types; it does not claim to type-check the examples.
"""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
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

    def test_typescript_examples_exhibit_the_recorded_runtime_behavior(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is unavailable; TypeScript runtime examples were not run")
        version = subprocess.run(
            [node, "--version"], check=True, capture_output=True, text=True, timeout=10
        ).stdout.strip()
        parts = tuple(int(part) for part in version.lstrip("v").split(".")[:2])
        if parts < (22, 6):
            self.skipTest("Node.js 22.6+ type stripping is required; examples were not run")
        with tempfile.TemporaryDirectory() as directory:
            for case in self.examples:
                if case["language"] != "typescript":
                    continue
                with self.subTest(case=case["id"]):
                    path = Path(directory) / (case["id"] + ".mts")
                    path.write_text(case["source"], encoding="utf-8")
                    result = subprocess.run(
                        [node, "--experimental-strip-types", str(path)],
                        check=False,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        cwd=directory,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, case["observed_stdout"])


if __name__ == "__main__":
    unittest.main()
