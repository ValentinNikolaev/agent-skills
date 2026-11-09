from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_skill_wrappers as generator  # noqa: E402
import validate_skills as validator  # noqa: E402


def make_skill(root: Path, words: int, lines: int = 1) -> generator.SourceSkill:
    directory = root / "alpha"
    (directory / "agents").mkdir(parents=True)
    (directory / "SKILL.md").write_text(
        "---\nname: alpha\ndescription: Fixture skill used to test the body size checks.\n---\n\n"
        + "\n".join(" ".join(["word"] * (words // lines)) for _ in range(lines))
        + "\n",
        encoding="utf-8",
    )
    (directory / "agents" / "openai.yaml").write_text(
        "interface:\n"
        '  display_name: "Alpha"\n'
        '  short_description: "Fixture skill for size tests"\n'
        '  default_prompt: "Use $alpha now."\n',
        encoding="utf-8",
    )
    return generator.read_source_skill(directory)


class BodySizeCeilingTests(unittest.TestCase):
    def errors_for(self, words: int, ceiling: int, lines: int = 1) -> list[str]:
        with tempfile.TemporaryDirectory() as temporary:
            skill = make_skill(Path(temporary), words, lines)
            with mock.patch.object(validator, "MAX_SKILL_BODY_WORDS", ceiling):
                return validator.validate_skill(skill)

    def test_body_at_the_ceiling_passes(self) -> None:
        self.assertEqual(self.errors_for(words=100, ceiling=100), [])

    def test_body_over_the_ceiling_fails_even_with_few_long_lines(self) -> None:
        errors = self.errors_for(words=101, ceiling=100, lines=1)
        self.assertEqual(len(errors), 1)
        self.assertIn("alpha/SKILL.md: body has 101 words", errors[0])
        self.assertIn("100-word ceiling", errors[0])

    def test_line_cap_still_applies_independently(self) -> None:
        errors = self.errors_for(words=600, ceiling=10_000, lines=600)
        self.assertEqual(len(errors), 1)
        self.assertIn("500-line guidance", errors[0])

    def test_stop_slop_is_not_required_and_not_canonical(self) -> None:
        self.assertFalse((REPO_ROOT / "agent-plugins" / "skills" / "stop-slop").exists())
        text = (REPO_ROOT / "scripts" / "validate_skills.py").read_text(encoding="utf-8")
        self.assertNotIn("stop-slop", text)


if __name__ == "__main__":
    unittest.main()
