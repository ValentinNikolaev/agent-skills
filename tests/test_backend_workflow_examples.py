"""Validate raw backend evaluation inputs, not model routing or review accuracy.

FastAPI runtime controls use installed dependencies only and otherwise skip.
No packages, servers, credentials, or network requests are provisioned here.
"""

import ast
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


FIXTURES = Path(__file__).resolve().parent / "fixtures"


class FastAPIReviewExamples(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((FIXTURES / "fastapi_review_examples.json").read_text(encoding="utf-8"))

    def test_examples_parse_and_have_discriminating_pairs(self):
        ids = [case["id"] for case in self.cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual({case["topic"] for case in self.cases}, {"response-filter", "stream-lifetime"})
        for case in self.cases:
            with self.subTest(case=case["id"]):
                ast.parse(case["source"] + "\n" + case["probe"])
                if case["expected_findings"]:
                    self.assertIn(case["location_line"], range(1, len(case["source"].splitlines()) + 1))
                else:
                    self.assertIsNone(case["location_line"])
        for topic in {case["topic"] for case in self.cases}:
            pair = [case for case in self.cases if case["topic"] == topic]
            with self.subTest(topic=topic):
                self.assertEqual(len(pair), 2)
                self.assertEqual(pair[0]["context"], pair[1]["context"])
                self.assertEqual(sum(bool(case["expected_findings"]) for case in pair), 1)
                self.assertNotEqual(pair[0]["observed_stdout"], pair[1]["observed_stdout"])

    def test_installed_fastapi_runtime_examples(self):
        missing = [name for name in ("fastapi", "httpx") if importlib.util.find_spec(name) is None]
        if missing:
            self.skipTest("FastAPI runtime examples unrun; missing " + ", ".join(missing))
        for case in self.cases:
            with self.subTest(case=case["id"]):
                result = subprocess.run(
                    [sys.executable, "-I", "-c", case["source"] + "\n" + case["probe"]],
                    check=False, capture_output=True, text=True, timeout=10,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, case["observed_stdout"])


class BackendWorkflowEvaluationInputs(unittest.TestCase):
    def test_raw_cases_have_explicit_obligations_and_limits(self):
        cases = json.loads((FIXTURES / "backend_workflow_cases.json").read_text(encoding="utf-8"))
        self.assertEqual(len(cases), len({case["id"] for case in cases}))
        self.assertTrue(any(case["skill"] is None for case in cases))
        self.assertEqual(
            {case["skill"] for case in cases if case["skill"]},
            {"code-review", "fastapi-development", "claude-api", "uv-project-workflow"},
        )
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["prompt"])
                for field in ("must_preserve", "must_verify", "must_not_do"):
                    self.assertTrue(case[field], field)
                    self.assertTrue(all(isinstance(value, str) and value.strip() for value in case[field]))
                self.assertFalse(set(case["must_preserve"]) & set(case["must_not_do"]))


if __name__ == "__main__":
    unittest.main()
