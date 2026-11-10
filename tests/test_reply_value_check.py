"""Verify the discussion-reply value check contract and its fixture cases.

These tests establish that the procedure text and the calibration cases are present
and consistent. They do not measure how a model applies the check.
"""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "agent-plugins" / "skills" / "discussion-reply"
SKILL = SKILL_DIR / "SKILL.md"
REFERENCE = SKILL_DIR / "references" / "contribution-value.md"
CASES = ROOT / "tests" / "fixtures" / "editorial_workflow_cases.json"

EXPECTED_VERDICTS = {
    "reply-value-minor-inconsistency": "revise",
    "reply-value-proven-decision": "pass",
    "reply-value-technical-mechanism": "pass",
    "reply-value-specific-support": "not-required",
    "reply-value-small-find-explanation-only": "revise",
}


class ReplyValueCheckTests(unittest.TestCase):
    def setUp(self):
        self.skill = SKILL.read_text(encoding="utf-8")
        self.reference = REFERENCE.read_text(encoding="utf-8")
        self.cases = {case["id"]: case for case in json.loads(CASES.read_text(encoding="utf-8"))}

    def test_skill_routes_analytical_replies_to_the_check_before_ratings(self):
        self.assertIn("(references/contribution-value.md)", self.skill)
        self.assertTrue(REFERENCE.is_file())
        self.assertIn("before ratings", self.skill)
        self.assertIn("unproven value blocks acceptance whatever the total", self.skill)

    def test_reference_requires_five_independent_answers_in_the_replys_words(self):
        for label in (
            "Question and link", "Reader gain", "Trace",
            "Effect of acting", "Marginal contribution",
        ):
            with self.subTest(label=label):
                self.assertIn(f"**{label}.**", self.reference)
        for phrase in (
            "each independent reviewer answers all five points",
            "Quote the reply's own words",
            "**pass** or **revise**",
            "confirmed",
            "assumed",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.reference)

    def test_reference_blocks_on_unproven_value_and_lets_the_coordinator_resolve_it(self):
        for phrase in (
            "failed gate, not a deduction",
            "does not override it",
            "strongest argument that the text is valuable",
            "one reviewer's unresolved revise verdict stands",
            "At final selection the coordinator repeats the check",
            "withdraw the idea, leave the slot empty",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.reference)

    def test_reference_keeps_short_support_and_does_not_ban_a_category(self):
        self.assertIn("Support, acknowledgment, humor, and a short human reaction are not gated", self.reference)
        self.assertIn("Do not ask for advice, a technical point, or an action.", self.reference)
        self.assertIn("No kind of observation is excluded in advance", self.reference)

    def test_reference_leaves_project_scoring_and_budgets_to_the_project(self):
        self.assertIn("adds no reviewer, rubric, weight, threshold, or repair", self.reference)
        self.assertIn("repair budget stay as the project set them", self.reference)
        self.assertIsNone(re.search(r"\b\d{2,3}\s*/\s*100\b|\b[0-5]\s*/\s*5\b", self.reference))

    def test_fixture_cases_cover_each_required_outcome(self):
        for case_id, verdict in EXPECTED_VERDICTS.items():
            with self.subTest(case=case_id):
                case = self.cases[case_id]
                self.assertEqual(case["skill"], "discussion-reply")
                self.assertEqual(case["value_verdict"], verdict)
                for field in ("request", "source"):
                    self.assertTrue(case[field].strip())
                for field in ("must_preserve", "must_verify", "must_not_do"):
                    self.assertTrue(case[field])
        self.assertEqual(
            sorted(set(EXPECTED_VERDICTS.values())), ["not-required", "pass", "revise"]
        )

    def test_matched_pair_differs_only_in_the_shown_consequence(self):
        weak = self.cases["reply-value-minor-inconsistency"]["source"]
        shown = self.cases["reply-value-proven-decision"]["source"]
        for text in (weak, shown):
            self.assertIn("Rule A", text)
            self.assertIn("precedence clause", text)
        self.assertIn("merge checklist requires that suite to pass", shown)
        self.assertNotIn("merge checklist", weak)

    def test_documentation_cases_do_not_adopt_a_category_rule(self):
        case = self.cases["reply-value-small-find-explanation-only"]
        self.assertTrue(any("documentation" in item for item in case["must_not_do"]))
        self.assertTrue(any("not because the finding concerns documentation" in item for item in case["must_verify"]))


if __name__ == "__main__":
    unittest.main()
