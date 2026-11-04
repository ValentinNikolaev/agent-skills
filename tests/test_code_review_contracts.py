"""Check executable review cases and the report contract, not model recall.

Only repository-owned fixture programs execute. The helper consumes reviewer
assessments; it does not infer findings from Python source or verify quotations.
"""

from copy import deepcopy
import difflib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "agent-plugins/skills/code-review/scripts/prepare_review_report.py"
SPEC = importlib.util.spec_from_file_location("review_report_contract", SCRIPT)
contract = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(contract)
CASES = json.loads((ROOT / "tests/fixtures/code_review_contract_cases.json").read_text(encoding="utf-8"))


def document(*candidates, mode="independent"):
    return {
        "verification_mode": mode,
        "references_read": ["references/finder-and-verifier.md"],
        "candidates": list(candidates),
    }


def finding(identity, *, priority="P2", category="correctness", verdict="CONFIRMED"):
    result = deepcopy(CASES[0]["candidate"])
    result.update(id=identity, priority=priority, category=category)
    assessment = result["assessments"][0]
    assessment["verdict"] = verdict
    if verdict == "PLAUSIBLE":
        assessment["confirmation"] = "Exercise the supported empty-store configuration."
    if verdict == "REFUTED":
        assessment.update(
            refutation="guard-in-diff",
            reason="The added None guard returns before the subscript for the proposed input.",
            evidence={"file": "lookup.py", "line": 2, "quote": "    if user is None:"},
        )
    if category == "conventions":
        result["rule"] = {"file": "AGENTS.md", "quote": "Return None for absent users."}
    return result


class ReviewContractTests(unittest.TestCase):
    def test_standard_and_deep_require_coordinator_reference_even_without_findings(self):
        for depth in ("standard", "deep"):
            for candidates in ((), (finding("CR-001"),)):
                for ledger in ([], ["references/review-shell.md"]):
                    value = document(*candidates)
                    value["references_read"] = ledger
                    with self.subTest(depth=depth, ledger=ledger, count=len(candidates)):
                        with self.assertRaisesRegex(contract.ContractError, "INCOMPLETE"):
                            contract.prepare_report(value, depth=depth, max_findings=0)
                value.pop("references_read")
                with self.assertRaisesRegex(contract.ContractError, "INCOMPLETE"):
                    contract.prepare_report(value, depth=depth)

    def test_reference_ledger_is_preserved_and_quick_can_omit_it(self):
        value = document()
        value["references_read"].append("references/review-shell.md")
        for depth in ("standard", "deep", "quick"):
            report = contract.prepare_report(value, depth=depth)
            self.assertEqual(report["references_read"], value["references_read"])
            self.assertIsNot(report["references_read"], value["references_read"])
        del value["references_read"]
        self.assertEqual(contract.prepare_report(value, depth="quick")["references_read"], [])
        for ledger in (None, "references/finder-and-verifier.md", [None], [""]):
            value["references_read"] = ledger
            with self.subTest(ledger=ledger), self.assertRaises(contract.ContractError):
                contract.prepare_report(value, depth="quick")

    def test_cli_missing_mandatory_reference_fails_without_report(self):
        value = document()
        del value["references_read"]
        for depth, status in (("standard", 2), ("deep", 2), ("quick", 0)):
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", "-", "--depth", depth],
                input=json.dumps(value), capture_output=True, text=True, timeout=5, check=False,
            )
            self.assertEqual(result.returncode, status, result.stderr)
            if status:
                self.assertEqual(result.stdout, "")
                self.assertIn("INCOMPLETE", result.stderr)
                self.assertIn("references/finder-and-verifier.md", result.stderr)
            else:
                self.assertEqual(json.loads(result.stdout)["references_read"], [])

    def test_removed_guard_case_and_control_exhibit_the_failure(self):
        case = CASES[0]
        diff = list(difflib.unified_diff(case["before"].splitlines(), case["after"].splitlines()))
        self.assertIn("-    if user is None:", diff)
        self.assertFalse(any(line.startswith("+") and "if user is None" in line for line in diff))
        self.assertEqual(case["candidate"]["angle"], "removed-behavior")
        self.assert_runtime_pair(case)
        report = contract.prepare_report(document(case["candidate"]))
        self.assertEqual([(item["id"], item["verdict"]) for item in report["findings"]], [("CR-001", "CONFIRMED")])
        self.assertTrue(report["has_blocker"])

    def assert_runtime_pair(self, case):
        for revision in ("before", "after"):
            result = subprocess.run(
                [sys.executable, "-I", "-c", case[revision] + "\n" + case["probe"]],
                capture_output=True, text=True, timeout=5, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, case[f"{revision}_stdout"])
        evidence = case["candidate"]["assessments"][0]["evidence"]
        self.assertEqual(case["after"].splitlines()[evidence["line"] - 1], evidence["quote"])

    def test_rare_reachable_nil_stays_plausible_not_retracted(self):
        case = CASES[1]
        self.assert_runtime_pair(case)
        report = contract.prepare_report(document(case["candidate"]))
        self.assertEqual(report["findings"][0]["verdict"], "PLAUSIBLE")
        self.assertTrue(report["findings"][0]["confirmation"])
        self.assertEqual(report["refuted"], [])
        self.assertEqual(report["rejected"], [])

    def test_conventions_reject_missing_rule_quote_or_path(self):
        candidate = finding("CR-003", category="conventions")
        valid = contract.prepare_report(document(candidate))
        self.assertEqual(len(valid["findings"]), 1)
        for rule in (None, {}, {"file": "AGENTS.md"}, {"quote": "Return None."}, {"file": "AGENTS.md", "quote": " "}):
            with self.subTest(rule=rule):
                candidate["rule"] = rule
                result = contract.prepare_report(document(candidate), depth="deep")
                self.assertEqual(result["findings"], [])
                self.assertEqual(result["rejected"][0]["id"], "CR-003")
                self.assertEqual(result["refuted"], [])

    def test_max_findings_orders_severity_then_correctness_before_cleanup(self):
        inputs = [
            finding("CR-001", category="cleanup"),
            finding("CR-002", category="conventions"),
            finding("CR-009", category="correctness", verdict="PLAUSIBLE"),
            finding("CR-008", category="security"),
            finding("CR-007", category="coverage"),
            finding("CR-006", priority="P1", category="conventions"),
            finding("CR-010", priority="P0"),
            finding("CR-003", priority="P3"),
        ]
        original = deepcopy(inputs)
        result = contract.prepare_report(document(*inputs), max_findings=4)
        self.assertEqual([item["id"] for item in result["findings"]], ["CR-010", "CR-006", "CR-008", "CR-009"])
        self.assertEqual(result["omitted_ids"], ["CR-007", "CR-001", "CR-002", "CR-003"])
        self.assertEqual(result["cut_count"], 4)
        self.assertEqual(result["retained_count"], 8)
        self.assertEqual(inputs, original)

    def test_zero_cap_does_not_clear_an_omitted_blocker(self):
        result = contract.prepare_report(document(finding("CR-001", priority="P1")), max_findings=0)
        self.assertEqual(result["findings"], [])
        self.assertEqual(result["cut_count"], 1)
        self.assertTrue(result["has_blocker"])

    def test_deep_keeps_one_non_refuted_vote_and_its_evidence(self):
        candidate = finding("CR-001", verdict="REFUTED")
        vote = finding("CR-001", verdict="PLAUSIBLE")["assessments"][0]
        vote["reviewer"] = "verifier-2"
        candidate["assessments"].append(vote)
        result = contract.prepare_report(document(candidate), depth="deep")
        self.assertEqual(result["findings"][0]["verdict"], "PLAUSIBLE")
        self.assertEqual(len(result["findings"][0]["assessments"]), 2)
        self.assertTrue(result["findings"][0]["confirmation"])
        self.assertEqual(result["refuted"], [])
        with self.assertRaises(contract.ContractError):
            contract.prepare_report(document(candidate), depth="standard")

    def test_refutation_requires_evidence_and_does_not_consume_cap(self):
        candidate = finding("CR-001", verdict="REFUTED")
        result = contract.prepare_report(document(candidate, finding("CR-002")), max_findings=1)
        self.assertEqual([item["id"] for item in result["findings"]], ["CR-002"])
        self.assertEqual(result["refuted"][0]["id"], "CR-001")
        self.assertEqual(result["cut_count"], 0)
        for field in ("evidence", "refutation", "reason"):
            broken = deepcopy(candidate)
            del broken["assessments"][0][field]
            with self.subTest(field=field), self.assertRaises(contract.ContractError):
                contract.prepare_report(document(broken))
        candidate["assessments"][0]["refutation"] = "unlikely-in-production"
        with self.assertRaises(contract.ContractError):
            contract.prepare_report(document(candidate))

    def test_independent_verification_requires_a_different_person(self):
        candidate = finding("CR-001")
        candidate["assessments"][0]["reviewer"] = candidate["finder"]
        with self.assertRaises(contract.ContractError):
            contract.prepare_report(document(candidate))
        self.assertEqual(contract.prepare_report(document(candidate, mode="inline"))["verification_mode"], "inline")

    def test_invalid_limits_duplicate_ids_and_missing_scenarios_fail(self):
        for limit in (-1, 1.5, True):
            with self.subTest(limit=limit), self.assertRaises(contract.ContractError):
                contract.prepare_report(document(finding("CR-001")), max_findings=limit)
        with self.assertRaises(contract.ContractError):
            contract.prepare_report(document(finding("CR-001"), finding("CR-001")))
        candidate = finding("CR-001")
        candidate["failure_scenario"] = ""
        with self.assertRaises(contract.ContractError):
            contract.prepare_report(document(candidate))

    def test_cli_stdin_and_invalid_contract_exit_status(self):
        for limit, expected_status in (("1", 0), ("-1", 2)):
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--input", "-", "--max-findings", limit],
                input=json.dumps(document(CASES[1]["candidate"])),
                capture_output=True, text=True, timeout=5, check=False,
            )
            self.assertEqual(result.returncode, expected_status, result.stderr)
            if expected_status == 0:
                self.assertEqual(json.loads(result.stdout)["findings"][0]["verdict"], "PLAUSIBLE")
            else:
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
