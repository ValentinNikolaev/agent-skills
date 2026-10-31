"""Check research/evaluation provenance, not prose quality or detector accuracy."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "agent-plugins/skills/ai-detector/references/research-evidence.json"
CASES = ROOT / "tests/fixtures/ai_style_research_cases.json"
RESULTS = ROOT / "tests/fixtures/ai_style_research_results.json"
LONG_CASES = ROOT / "tests/fixtures/humanizer_longform_cases.json"
LONG_RESULTS = ROOT / "tests/fixtures/humanizer_longform_results.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class ResearchRecordTests(unittest.TestCase):
    def test_seven_pinned_sources_and_published_inventory_counts(self) -> None:
        data = read_json(EVIDENCE)
        sources = data["sources"]
        self.assertEqual(len(sources), data["source_count"])
        self.assertEqual(len(sources), 7)
        self.assertEqual(len({s["id"] for s in sources}), 7)
        self.assertEqual(len({s["url"] for s in sources}), 7)
        for source in sources:
            with self.subTest(source=source["id"]):
                self.assertTrue(source["url"].startswith("https://"))
                self.assertTrue(source["license"])
                self.assertTrue(source["version"])
                self.assertTrue(source["transfer"])
        linguistic = data["research"]["linguistic"]
        groups = linguistic["source_2606"]["feature_groups"]
        self.assertEqual(len(groups), 11)
        self.assertEqual(sum(group["count"] for group in groups), 284)
        # The appendix exposes 29 names, despite the paper's claimed total of 31.
        named = linguistic["source_2505"]["inventory_appendix_table_2"]
        self.assertEqual(len(named), 29)
        self.assertEqual(len({row[0] for row in named}), 29)

    def test_rankings_cover_only_comparable_reported_measurements(self) -> None:
        data = read_json(EVIDENCE)
        rankings = data["within_source_rankings"]
        features = data["research"]["statistical"]["diveye"]["features"]
        recorded = {item["feature"]: item["auc_drop"] for item in rankings["diveye_leave_one_out_auc_drop"]["items"]}
        self.assertEqual(recorded, {f["id"]: f["leave_one_out_auc_drop"] for f in features})
        self.assertEqual(len(recorded), 9)
        mental = data["research"]["discourse"]["sources"][1]
        inventories = {
            "mental_health_lexicosemantic": [(row[0], row[3]) for row in mental["lexicosemantic_inventory"]],
            "mental_health_liwc": [(row[0], row[4]) for group in mental["liwc_inventory"].values() for row in group],
        }
        for key, inventory in inventories.items():
            with self.subTest(ranking=key):
                expected = {name: value for name, value in inventory if value is not None}
                items = rankings[key]["items"]
                self.assertEqual({i["feature"]: i["signed_d"] for i in items}, expected)
                magnitudes = [abs(i["signed_d"]) for i in items]
                self.assertEqual(magnitudes, sorted(magnitudes, reverse=True))
                for item in items:
                    self.assertEqual(item["rank"], magnitudes.index(abs(item["signed_d"])) + 1)

    def test_frozen_cases_have_disjoint_ids_and_explicit_scope(self) -> None:
        data = read_json(CASES)
        cases = data["cases"]
        self.assertFalse(data["protocol"]["external_submission"])
        self.assertEqual(len(cases), len({case["id"] for case in cases}))
        self.assertEqual(sum(c["split"] == "development" for c in cases), 6)
        self.assertEqual(sum(c["split"] == "holdout" for c in cases), 10)
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertIn(case["skill"], {"humanizer", "ai-detector"})
                self.assertTrue(case["request"])
                self.assertTrue(case["text"])
                self.assertTrue(case["constraints"])

    def test_evaluation_retains_complete_exact_outputs_and_iteration_history(self) -> None:
        data = read_json(RESULTS)
        # Git may check out CRLF on Windows; the frozen corpus uses UTF-8/LF.
        corpus = CASES.read_text(encoding="utf-8").encode("utf-8")
        self.assertEqual(data["cases_sha256"], hashlib.sha256(corpus).hexdigest())
        expected = {case["id"] for case in read_json(CASES)["cases"]}
        expected.update(case["id"] for case in data["historical_regression"]["cases"])
        for phase in ("baseline", "candidate"):
            records = data[phase]["records"]
            self.assertEqual({r["case_id"] for r in records}, expected)
            self.assertEqual(len(records), len(expected))
            for record in records:
                with self.subTest(phase=phase, case=record["case_id"]):
                    self.assertTrue(record["output"])
                    digest = hashlib.sha256(record["output"].encode("utf-8")).hexdigest()
                    self.assertEqual(record["output_sha256"], digest)
        iterations = data["iterations"]
        self.assertEqual([r["id"] for r in iterations], [f"I{i:02}" for i in range(1, 7)])
        for iteration in iterations:
            self.assertEqual(len(iteration["advisor_assessments"]), 3)
            self.assertTrue(iteration["peer_review"])
            self.assertTrue(iteration["decision"])
        self.assertEqual(len(data["final_comparison_reviewers"]), 3)
        self.assertEqual(len(data["nonauthor_agents"]), 4)
        self.assertFalse(data["claims"]["detection_accuracy_measured"])
        self.assertFalse(data["claims"]["human_reader_validation"])

    def test_longform_extension_preserves_inputs_first_outputs_and_reviewer_roles(self) -> None:
        cases = read_json(LONG_CASES)["cases"]
        data = read_json(LONG_RESULTS)
        corpus = LONG_CASES.read_text(encoding="utf-8").encode("utf-8")
        self.assertEqual(data["cases_sha256"], hashlib.sha256(corpus).hexdigest())
        expected = {case["id"] for case in cases}
        self.assertEqual(len(expected), 6)
        editor_inputs = data["editor_input"]["cases"]
        self.assertEqual({c["id"] for c in editor_inputs}, expected)
        for case in editor_inputs:
            self.assertEqual(set(case), {"id", "language", "request", "text"})
        records = [r for executor in data["executions"] for r in executor["records"]]
        self.assertEqual(len(records), 12)
        self.assertEqual({(r["case_id"], r["package"]) for r in records},
                         {(case, package) for case in expected for package in ("P", "Q")})
        for record in records:
            digest = hashlib.sha256(record["output"].encode("utf-8")).hexdigest()
            self.assertEqual(record["output_sha256"], digest)
        self.assertEqual(len(data["reviews"]), 4)
        self.assertEqual(sum(r["independent_of_fresh_outputs"] for r in data["reviews"]), 2)
        for review in data["reviews"]:
            self.assertEqual({r["case_id"] for r in review["assessment"]["records"]}, expected)
        for repair in data["post_review_repairs"]:
            original = next(r for r in records if r["case_id"] == repair["case"]["id"]
                            and r["package"] == repair["package"])
            self.assertEqual(repair["initial_output"], original["output"])
        self.assertEqual(len(data["repair_advisors"]), 3)
        self.assertTrue(data["repair_peer_review"])
        self.assertFalse(data["claims"]["general_skill_superiority_established"])


if __name__ == "__main__":
    unittest.main()
