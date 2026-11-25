"""Evidence integrity checks for the portable education baseline."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "agent-plugins/shared/education/evidence.json"
UPDATE = ROOT / "agent-plugins/skills/education-learning-science/examples/research-update.json"
EXPORT = ROOT / "agent-plugins/skills/education-learning-science/examples/project-export.json"
CONTRACTS = ROOT / "agent-plugins/shared/education/contracts.json"


class EducationEvidenceTests(unittest.TestCase):
    def test_rules_have_traceable_sources_and_operating_boundaries(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        source_ids = [source["id"] for source in registry["sources"]]
        rule_ids = [rule["id"] for rule in registry["rules"]]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertEqual(len(rule_ids), len(set(rule_ids)))
        self.assertTrue({"R-retrieval", "R-spacing", "R-examples", "R-feedback", "R-access", "R-assistance"} <= set(rule_ids))

        for source in registry["sources"]:
            for field in ("design", "population", "setting", "subject", "age", "intervention", "comparator", "outcomes", "follow_up", "limitations", "risk_of_bias", "consistency", "directness", "certainty", "access", "source_version", "verified_at"):
                self.assertIn(field, source)
        for rule in registry["rules"]:
            self.assertTrue(rule["source_ids"])
            self.assertTrue(set(rule["source_ids"]) <= set(source_ids))
            for field in ("version", "kind", "rationale", "scope", "conditions", "counterexamples", "contraindications", "uncertainty", "evaluation_method", "review_date"):
                self.assertTrue(rule[field], (rule["id"], field))

    def test_conflicting_research_does_not_erase_rejected_attempt(self):
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        update = json.loads(UPDATE.read_text(encoding="utf-8"))
        rules = {rule["id"]: rule for rule in registry["rules"]}
        self.assertEqual(update["proposal"]["status"], "rejected")
        self.assertEqual(update["baseline_rule_version"], rules[update["baseline_rule_id"]]["version"])
        self.assertTrue(set(update["source_ids"]) <= set(rules[update["baseline_rule_id"]]["source_ids"]))
        self.assertTrue(update["source_observations_preserved"])
        self.assertEqual(update["resumed_proposal"]["prior_attempt_id"], update["proposal"]["id"])
        self.assertEqual(update["resumed_proposal"]["decision"], "rejected")
        self.assertIsNone(update["learner_outcomes"])

    def test_project_export_uses_shared_contract_fields(self):
        contracts = json.loads(CONTRACTS.read_text(encoding="utf-8"))
        example = json.loads(EXPORT.read_text(encoding="utf-8"))
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        known_sources = {source["id"] for source in registry["sources"]}
        known_rules = {rule["id"] for rule in registry["rules"]}
        refs = {f'{artifact["id"]}@{artifact["revision"]}' for artifact in example["artifacts"]}
        self.assertEqual(example["schema_version"], contracts["schema_version"])
        for artifact in example["artifacts"]:
            self.assertEqual(artifact["producer"], "learning-science")
            self.assertTrue(set(contracts["artifacts"][artifact["kind"]]["fields"]) <= set(artifact["data"]))
            self.assertTrue(set(artifact["data"].get("sources", [])) <= known_sources)
            self.assertTrue(set(artifact["data"].get("source_ids", [])) <= known_sources)
            self.assertTrue(set(artifact["data"].get("rule_refs", [])) <= refs)
            if artifact["kind"] == "PedagogicalRule":
                self.assertIn(artifact["data"]["rule_id"], known_rules)


if __name__ == "__main__":
    unittest.main()
