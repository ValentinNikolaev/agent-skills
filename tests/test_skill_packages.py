from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import validate_skills  # noqa: E402


class SkillPackageTests(unittest.TestCase):
    def test_canonical_packages_pass_repository_validator(self) -> None:
        errors = validate_skills.validate_repository(REPO_ROOT)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_every_bundled_python_helper_has_a_safe_help_path(self) -> None:
        scripts = sorted(
            (REPO_ROOT / "agent-plugins" / "skills").glob("*/scripts/*.py")
        ) + sorted((REPO_ROOT / "agent-plugins" / "shared").rglob("*.py"))
        self.assertTrue(scripts, "expected at least one bundled helper")
        for script in scripts:
            with self.subTest(script=script.relative_to(REPO_ROOT)):
                result = subprocess.run(
                    [sys.executable, str(script), "--help"],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
                )

    def test_memory_validator_has_one_canonical_source(self) -> None:
        shared = (
            REPO_ROOT
            / "agent-plugins"
            / "shared"
            / "memory"
            / "validate_memory.py"
        )
        self.assertTrue(shared.is_file())
        redundant = sorted(
            (REPO_ROOT / "agent-plugins" / "skills").glob(
                "*/scripts/validate_memory.py"
            )
        )
        self.assertEqual(redundant, [])

    def test_frontmatter_rejects_unparsed_top_level_syntax(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = Path(temporary) / "fixture"
            (skill_dir / "agents").mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: fixture\n"
                "description: Use this fixture to prove strict frontmatter parsing.\n"
                "this is not valid yaml\n"
                "---\n\n# Fixture\n",
                encoding="utf-8",
            )
            (skill_dir / "agents" / "openai.yaml").write_text(
                "interface:\n"
                "  display_name: \"Fixture\"\n"
                "  short_description: \"Validate a strict fixture package\"\n"
                "  default_prompt: \"Use $fixture to validate this package.\"\n",
                encoding="utf-8",
            )
            skill = validate_skills.wrappers.read_source_skill(skill_dir)
            errors = validate_skills.validate_skill(skill)
            self.assertTrue(
                any("expected an unindented" in error for error in errors), errors
            )

    def test_openai_fields_must_be_direct_interface_children(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = Path(temporary) / "fixture"
            (skill_dir / "agents").mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: fixture\n"
                "description: Use this fixture to prove interface field scoping.\n"
                "---\n\n# Fixture\n",
                encoding="utf-8",
            )
            (skill_dir / "agents" / "openai.yaml").write_text(
                "interface:\n"
                "unrelated:\n"
                "  display_name: \"Fixture\"\n"
                "  short_description: \"Validate a scoped fixture package\"\n"
                "  default_prompt: \"Use $fixture to validate this package.\"\n",
                encoding="utf-8",
            )
            skill = validate_skills.wrappers.read_source_skill(skill_dir)
            errors = validate_skills.validate_openai_yaml(skill)
            for key in ("display_name", "short_description", "default_prompt"):
                self.assertTrue(
                    any(f"interface.{key}" in error for error in errors), errors
                )


if __name__ == "__main__":
    unittest.main()
