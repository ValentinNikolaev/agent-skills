from __future__ import annotations

import re
import shlex
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "agent-plugins" / "skills"
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import validate_skills  # noqa: E402


class GoSkillContractTests(unittest.TestCase):
    """Check packaging and safety contracts, not model review accuracy."""

    def test_specialists_are_portable_passive_packages(self) -> None:
        for name in ("go-security-audit", "go-benchmark"):
            with self.subTest(skill=name):
                directory = SKILLS_ROOT / name
                skill = validate_skills.wrappers.read_source_skill(directory)
                self.assertEqual(validate_skills.validate_skill(skill), [])
                self.assertEqual(validate_skills.validate_openai_yaml(skill), [])
                files = [path for path in directory.rglob("*") if path.is_file()]
                self.assertFalse(any(path.is_symlink() for path in directory.rglob("*")))
                self.assertTrue(all(
                    path.suffix in {".md", ".yaml"} or path.name.startswith("LICENSE.")
                    for path in files
                ), "new specialists must not silently bundle executable tools")
                fields, keys, errors = validate_skills.parse_portable_frontmatter(skill.frontmatter)
                self.assertEqual(errors, [])
                self.assertEqual(set(keys), {"name", "description"})
                self.assertLessEqual(len(fields["description"]), 100)
                self.assertIn("not PR review", fields["description"])

    def test_scoped_license_copies_retain_upstream_notices(self) -> None:
        licenses = {
            "LICENSE.samber-cc-skills-golang": (
                "Copyright (c) 2026 Samuel Berthe",
                ("go-security-audit", "go-benchmark", "review-arch", "code-simplification",
                 "debugging-and-error-recovery", "vet-dependency", "console-ux-design"),
            ),
            "LICENSE.spf13-go-skills": (
                "Copyright (c) 2026 Steve Francia",
                ("review-spec", "api-and-interface-design", "deprecation-and-migration",
                 "console-ux-design"),
            ),
        }
        for filename, (copyright_notice, packages) in licenses.items():
            copies = []
            for package in packages:
                with self.subTest(package=package, license=filename):
                    content = (SKILLS_ROOT / package / filename).read_text(encoding="utf-8")
                    self.assertIn(copyright_notice, content)
                    self.assertIn("Permission is hereby granted, free of charge", content)
                    self.assertIn('THE SOFTWARE IS PROVIDED "AS IS"', content)
                    copies.append(content)
            self.assertEqual(len(set(copies)), 1, "scoped copies must retain the same license")

    def test_benchmark_example_selects_one_case_and_skips_unrelated_tests(self) -> None:
        body = (SKILLS_ROOT / "go-benchmark" / "SKILL.md").read_text(encoding="utf-8")
        command = re.search(r"`(go test -run [^`]+)`", body)
        self.assertIsNotNone(command, "include a scoped measurement example")
        tokens = shlex.split(command.group(1))
        self.assertEqual(tokens[tokens.index("-run") + 1], "^$")
        pattern = tokens[tokens.index("-bench") + 1]
        self.assertIsNotNone(re.fullmatch(pattern, "BenchmarkParse"))
        self.assertIsNone(re.fullmatch(pattern, "BenchmarkUnrelated"))
        count = next((token.split("=", 1)[1] for token in tokens if token.startswith("-count=")), None)
        if count is None:
            count = tokens[tokens.index("-count") + 1]
        self.assertGreater(int(count), 1)
        self.assertNotIn("./...", tokens)

    def test_security_reference_does_not_claim_text_template_autoescaping(self) -> None:
        body = (SKILLS_ROOT / "go-security-audit" / "references" / "audit-domains.md").read_text(
            encoding="utf-8"
        )
        self.assertRegex(body, r"`html/template`[^\n]+escaping; `text/template` does not")
        workflow = (SKILLS_ROOT / "go-security-audit" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Retract a candidate", workflow)
        self.assertIn("Missing redundant defense alone is not a confirmed vulnerability", workflow)
        self.assertIn("do not edit code, add safety comments, install scanners", workflow)

    def test_specialists_define_incomplete_and_incomparable_results(self) -> None:
        audit = (SKILLS_ROOT / "go-security-audit" / "SKILL.md").read_text(encoding="utf-8")
        benchmark = (SKILLS_ROOT / "go-benchmark" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("essential in-scope evidence remains missing", audit)
        self.assertIn("even if some findings are confirmed", audit)
        self.assertIn("empty selection, missing baseline, or invalid execution", benchmark)
        self.assertIn("Do not attribute toolchain or fixture differences to the implementation", benchmark)


if __name__ == "__main__":
    unittest.main()
