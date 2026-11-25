"""Contract, content and recovery checks for the public synthetic education examples."""

import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "agent-plugins" / "skills"
ORCHESTRATOR = SKILLS / "education-orchestrator"
EXAMPLES = ROOT / "docs" / "education" / "examples"
sys.path.insert(0, str(ORCHESTRATOR / "scripts"))
import workflow as wf
from contracts import Invalid, check_bundle, load, resources

PRESETS = load(wf.PRESETS)
MOTION = EXAMPLES / "motion" / "project.json"
ADMISSION = EXAMPLES / "admission" / "project.json"
LANGUAGE = EXAMPLES / "language-learning-trace.json"
SCIENCE = SKILLS / "education-learning-science" / "examples" / "project-export.json"
GOVERNANCE = EXAMPLES / "governance-project.json"


def artifact(bundle, key):
    return next(a for a in bundle["artifacts"] if a["id"] == key)


def complete_stage(state, node_id, bundle, refs=None):
    node = state["nodes"][node_id]
    if refs is None:
        refs = [f"{a['id']}@{a['revision']}" for a in bundle["artifacts"] if a["kind"] in node["outputs"]]
    running = wf.advance(state, "start", node_id, reason="inputs checked")
    return wf.advance(running, "pass", node_id, bundle=bundle, refs=refs)


def completed(preset, bundle):
    state = wf.new_plan("sample", PRESETS[preset])
    for node in PRESETS[preset]:
        state = complete_stage(state, node["id"], bundle)
    return state


class EducationContracts(unittest.TestCase):
    def test_every_contract_has_a_valid_example_and_detects_missing_fields(self):
        seen = set()
        for path in (MOTION, ADMISSION, LANGUAGE, SCIENCE, GOVERNANCE):
            bundle = load(path)
            check_bundle(bundle)
            for a in bundle["artifacts"]:
                if a["kind"] in seen:
                    continue
                seen.add(a["kind"])
                broken = copy.deepcopy(bundle)
                key = next(iter(load(resources() / "contracts.json")["artifacts"][a["kind"]]["fields"]))
                del artifact(broken, a["id"])["data"][key]
                with self.subTest(kind=a["kind"]), self.assertRaises(Invalid):
                    check_bundle(broken)
        self.assertEqual(seen, set(load(resources() / "contracts.json")["artifacts"]))

    def test_official_alignment_requires_source_edition_and_anchor(self):
        for defect in ("missing source", "no edition", "unverified", "no anchor"):
            b = load(ADMISSION)
            if defect == "missing source":
                artifact(b, "preparation")["data"]["official_sources"] = []
            elif defect == "no edition":
                artifact(b, "preparation")["data"]["edition"] = None
            elif defect == "unverified":
                b["sources"][0]["verification"] = "conflicting editions"
            else:
                artifact(b, "curriculum")["data"]["requirements"][0]["anchor"] = None
            with self.subTest(defect), self.assertRaises(Invalid):
                check_bundle(b)
        b = load(ADMISSION)
        # A missing current exam spec can still support explicitly provisional local practice.
        prep = artifact(b, "preparation")
        prep["status"] = "provisional"
        prep["data"].update(alignment="provisional", edition=None, official_sources=[])
        check_bundle(b)

    def test_versions_identity_edges_and_ownership(self):
        for defect in ("duplicate", "stale", "version", "owner", "dangling", "cycle", "rule"):
            b = load(MOTION)
            g = artifact(b, "graph")["data"]
            if defect == "duplicate":
                b["artifacts"].append(b["artifacts"][0])
            elif defect == "stale":
                artifact(b, "blueprint")["revision"] += 1
            elif defect == "version":
                b["schema_version"] = 2
            elif defect == "owner":
                artifact(b, "item-1")["producer"] = "materials-review"
            elif defect == "dangling":
                g["edges"][0]["before"] = "unknown"
            elif defect == "cycle":
                e = g["edges"][0]
                g["edges"].append({"before": e["after"], "after": e["before"], "relation": "strict"})
            else:
                artifact(b, "plan")["data"]["rules"] = ["invented"]
            with self.subTest(defect), self.assertRaises(Invalid):
                check_bundle(b)

    def test_coverage_and_review_cannot_be_overridden(self):
        b = load(MOTION)
        artifact(b, "item-2")["data"]["objectives"] = ["goal-1@1"]
        artifact(b, "item-2")["depends_on"].append("goal-1@1")
        with self.assertRaisesRegex(Invalid, "missing teaching.*assessment"):
            check_bundle(b, alignment=True)
        for resolution in ("open", "accepted-risk", "fixed"):
            b = load(MOTION)
            artifact(b, "review")["data"]["findings"] = [{
                "target": "item-1@1", "location": "key", "severity": "critical",
                "evidence": "Returned displacement in place of distance", "fix": "Recompute both legs",
                "owner": "assessment-design", "status": resolution, "retest": None}]
            with self.subTest(resolution), self.assertRaises(Invalid):
                check_bundle(b)

    def test_physics_and_algebra_stems_keys_and_learner_deliverables(self):
        for path in (MOTION, ADMISSION):
            b = load(path)
            learner = (path.parent / "learner.md").read_text(encoding="utf8")
            teacher = (path.parent / "teacher.md").read_text(encoding="utf8")
            for a in b["artifacts"]:
                if a["kind"] == "AssessmentItem":
                    self.assertIn(a["data"]["prompt"], learner)
                    self.assertIn(a["data"]["key"], teacher)
                    self.assertNotIn(a["data"]["rationale"], learner)
                if a["kind"] == "LearningMaterial":
                    for section in a["data"]["sections"]:
                        self.assertIn(section["body"], learner)
                        self.assertIn(section["practice"], learner)
            check_bundle(b, alignment=True)
        physics = load(MOTION)
        key1 = artifact(physics, "item-1")["data"]["key"]
        self.assertEqual([int(n) for n in re.findall(r"[+]?[0-9]+", key1)],
                         [abs(8 - 0) + abs(3 - 8), 3 - 0])
        self.assertEqual(int(re.search(r"\d+", artifact(physics, "item-2")["data"]["key"])[0]), 18 / 6 * 4)
        maths = load(ADMISSION)
        for key, linear, constant in (("item-1", -5, 6), ("item-2", 1, -12)):
            solution = artifact(maths, key)["data"]["key"].replace("−", "-")
            numbers = [int(n) for n in re.findall(r"-?\d+", solution)]
            roots = numbers if key == "item-1" else numbers[::2]
            self.assertEqual(len(set(roots)), 2)
            self.assertTrue(all(x*x + linear*x + constant == 0 for x in roots))
            if key == "item-2":
                self.assertEqual(numbers[1::2], [0, 0])

    def test_private_data_never_enters_count_export(self):
        b = load(LANGUAGE)
        b["private_note"] = "sample-private-address"
        report = wf.inventory(b)
        self.assertEqual(set(report), {"LearningMaterial", "LearningObjective", "AssessmentItem", "AssessmentBlueprint"})
        self.assertTrue(all(type(value) is int for value in report.values()))
        self.assertNotIn("sample-private-address", json.dumps(report))

    def test_event_denominators_assistance_and_absence(self):
        b = load(LANGUAGE)
        pinned = check_bundle(b)
        report = next(a["data"] for a in pinned.values() if a["kind"] == "AnalyticsReport")
        events = [pinned[ref]["data"] for ref in report["events"]]
        groups = [
            [e for e in events if e["attempt"] == 1 and e["assistance"] == "none"],
            [e for e in events if e["assistance"] == "hint"],
        ]
        groups.extend([e for e in events if e["assistance"] == "none" and e["occasion"] == occasion]
                      for occasion in ("transfer", "delayed"))
        self.assertEqual([(sum(e["outcome"] == "correct" for e in g), len(g)) for g in groups],
                         [(m["numerator"], m["denominator"]) for m in report["measures"]])
        self.assertTrue(any(a["kind"] == "LearnerProfile" and not a["data"]["observations"]
                            for a in pinned.values()))
        self.assertEqual(sum(e["outcome"] == "correct" for e in events), 2)


class EducationWorkflows(unittest.TestCase):
    def test_all_presets_and_two_complete_projects_survive_process_boundary(self):
        for preset, nodes in PRESETS.items():
            with self.subTest(preset):
                self.assertTrue(wf.new_plan(preset, nodes)["nodes"])
        for preset, path in (("author", MOTION), ("admission", ADMISSION), ("research", GOVERNANCE)):
            with self.subTest(preset), tempfile.TemporaryDirectory() as temp:
                journal = Path(temp) / "state"
                state = wf.new_plan("demo", PRESETS[preset])
                wf.save(journal, state)
                for node in PRESETS[preset]:
                    state = complete_stage(wf.latest(journal), node["id"], load(path))
                    wf.save(journal, state)
                restored = wf.latest(journal)
                self.assertTrue(all(n["status"] == "passed" for n in restored["nodes"].values()))
                with self.assertRaises(FileExistsError):
                    wf.save(journal, restored)

    def test_reopen_and_refresh_only_affected_descendants(self):
        b = load(MOTION)
        state = completed("author", b)
        wrong = copy.deepcopy(b)
        artifact(wrong, "item-1")["data"]["key"] = "different"
        with self.assertRaisesRegex(Invalid, "new revision"):
            wf.advance(state, "refresh", bundle=wrong)
        b["artifacts"] = [a for a in b["artifacts"] if a["kind"] != "ReviewReport"]
        a = artifact(b, "item-1")
        a["revision"] = 2
        a["data"]["key"] += " Рух завершується праворуч від початкової точки."
        stale = wf.advance(state, "refresh", bundle=b)
        self.assertEqual({n for n, v in stale["nodes"].items() if v["status"] == "stale"}, {"items", "review"})
        with self.assertRaisesRegex(Invalid, "upstream"):
            wf.advance(stale, "start", "review")
        fresh = complete_stage(stale, "items", b)
        review = copy.deepcopy(artifact(load(MOTION), "review"))
        review["revision"] = 2
        for refs in (review["depends_on"], review["data"]["targets"]):
            refs[refs.index("item-1@1")] = "item-1@2"
        b["artifacts"].append(review)
        fresh = complete_stage(fresh, "review", b)
        self.assertEqual(fresh["nodes"]["review"]["status"], "passed")
        self.assertIn("item-1@1", fresh["versions"])

    def test_repair_preserves_frozen_input_audit_after_new_revision(self):
        b = load(MOTION)
        original = artifact(b, "guide")
        original["data"]["sections"][0]["body"] = "Seeded incorrect equivalence of path and displacement."
        report = artifact(b, "review")
        report["id"] = "audit-report"
        report["data"].update(targets=["guide@1"], decision="block", findings=[{
            "target":"guide@1", "location":"section-1", "severity":"critical", "evidence":"contradicts the return journey",
            "fix":"distinguish path length from displacement", "owner":"instructional-design", "status":"open", "retest":None}])
        state = complete_stage(wf.new_plan("repair", PRESETS["repair"]), "audit", b)
        fixed = load(MOTION)
        artifact(fixed, "guide")["revision"] = 2
        retest = artifact(fixed, "review")
        retest["depends_on"] = ["guide@2"]
        retest["data"]["targets"] = ["guide@2"]
        state = wf.advance(state, "refresh", bundle=fixed)
        state = complete_stage(state, "revise", fixed)
        with self.assertRaisesRegex(Invalid, "still need a retest"):
            complete_stage(state, "review", fixed)
        retest["data"]["retests"] = [{"finding": "audit-report@1#1", "target": "guide@2",
                                      "evidence": "Recomputed the return path and signed displacement separately."}]
        state = complete_stage(state, "review", fixed)
        self.assertEqual(state["nodes"]["audit"]["status"], "passed")
        self.assertIn("audit-report@1", state["versions"])
        self.assertIn("guide@2", state["versions"])

    def test_blocked_reviewer_and_high_stakes_gate(self):
        b = load(MOTION)
        state = completed("author", b)
        state = wf.advance(state, "reopen", "review", reason="Requested high-stakes use")
        state["nodes"]["review"]["high_stakes"] = True
        with self.assertRaisesRegex(Invalid, "qualified human"):
            complete_stage(state, "review", b)
        running = wf.advance(state, "start", "review")
        for _ in range(2):
            failed = wf.advance(running, "fail", "review", reason="private audit record")
            running = wf.advance(failed, "start", "review", reason="additional evidence") if failed["nodes"]["review"]["attempts"] < 3 else None
            if running is None:
                break
        with self.assertRaisesRegex(Invalid, "attempt limit"):
            wf.advance(failed, "start", "review", reason="same evidence")
        with self.assertRaises(Invalid):
            wf.advance(state, "skip", "review", reason="skip requested")

    def test_installed_skills_are_self_contained_with_no_overlay_drift(self):
        shared = resources()
        for platform in ("claude", "codex"):
            packages = sorted((ROOT / platform / "skills").glob("education-*"))
            self.assertEqual(len(packages), 10)
            with tempfile.TemporaryDirectory() as temp:
                for package in packages:
                    with self.subTest(platform, package=package.name):
                        standalone = shutil.copytree(package, Path(temp) / package.name)
                        for filename in ("evidence.json", "contracts.json", "adapters.json"):
                            self.assertEqual(load(standalone / "references" / "education" / filename), load(shared / filename))
                        if package.name == "education-orchestrator":
                            result = subprocess.run([sys.executable, str(standalone / "scripts" / "workflow.py"),
                                                     "check", str(MOTION), "--alignment"], capture_output=True, text=True)
                            self.assertEqual(result.returncode, 0, result.stderr)
