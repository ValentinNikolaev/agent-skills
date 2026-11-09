from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_release_notes as release_notes  # noqa: E402
import generate_skill_wrappers as generator  # noqa: E402


def write_skill(root: Path, name: str, body: str = "# Skill\n") -> Path:
    directory = root / "agent-plugins" / "skills" / name
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Fixture skill {name} for projection tests.\n---\n\n{body}",
        encoding="utf-8",
    )
    return directory


def write_manifests(root: Path, version: str = "1.2.3") -> None:
    for platform in ("claude", "codex"):
        directory = root / f".{platform}-plugin"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "plugin.json").write_text(
            json.dumps({"name": "fixture", "version": version}) + "\n",
            encoding="utf-8",
        )


def manifest_versions(root: Path) -> dict[str, str]:
    return {
        platform: json.loads(
            (root / f".{platform}-plugin" / "plugin.json").read_text(encoding="utf-8")
        )["version"]
        for platform in ("claude", "codex")
    }


def tree_digest(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): generator.hash_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def core(version: str) -> str:
    return version.split("+", 1)[0]


def run_quiet(argv: list[str]) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = generator.run(argv)
    return code, out.getvalue()


class DryRunProjectionTests(unittest.TestCase):
    def prepare(self) -> tempfile.TemporaryDirectory:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        write_skill(root, "alpha")
        write_manifests(root)
        return temporary

    def real_run_versions(self, root: Path, *flags: str) -> dict[str, str]:
        """Run real generation on a copy and return the resulting version cores."""
        with tempfile.TemporaryDirectory() as copy_name:
            copy = Path(copy_name) / "repo"
            shutil.copytree(root, copy)
            code, _out = run_quiet(["--repo-root", str(copy), *flags])
            self.assertEqual(code, 0)
            return {key: core(value) for key, value in manifest_versions(copy).items()}

    def projected_versions(self, root: Path, *, clean: bool = True) -> dict[str, str]:
        before = manifest_versions(root)
        return {
            item.platform: (item.projected or core(before[item.platform]))
            for item in generator.project_release(root, clean=clean)
        }

    def test_projection_matches_a_real_run_through_each_stage(self) -> None:
        with self.prepare() as temporary:
            root = Path(temporary)
            # Stage 1: nothing generated yet, so every file is added: major.
            self.assertEqual(
                self.projected_versions(root), self.real_run_versions(root, "--clean")
            )
            self.assertTrue(
                all(item.bump == "major" for item in generator.project_release(root))
            )
            self.assertEqual(run_quiet(["--repo-root", str(root)])[0], 0)

            # Stage 2: generated tree is current: no change.
            self.assertTrue(
                all(item.bump is None for item in generator.project_release(root))
            )
            self.assertEqual(
                self.projected_versions(root), self.real_run_versions(root, "--clean")
            )

            # Stage 3: an edited body changes a file: minor.
            skill = root / "agent-plugins" / "skills" / "alpha" / "SKILL.md"
            skill.write_text(skill.read_text(encoding="utf-8") + "\nMore.\n", encoding="utf-8")
            self.assertEqual(
                self.projected_versions(root), self.real_run_versions(root, "--clean")
            )
            self.assertTrue(
                all(item.bump == "minor" for item in generator.project_release(root))
            )
            self.assertEqual(run_quiet(["--repo-root", str(root)])[0], 0)

            # Stage 4: an added reference file is major.
            references = root / "agent-plugins" / "skills" / "alpha" / "references"
            references.mkdir()
            (references / "note.md").write_text("# Note\n", encoding="utf-8")
            skill.write_text(
                skill.read_text(encoding="utf-8") + "\n[note](references/note.md)\n",
                encoding="utf-8",
            )
            self.assertEqual(
                self.projected_versions(root), self.real_run_versions(root, "--clean")
            )
            self.assertTrue(
                all(item.bump == "major" for item in generator.project_release(root))
            )

    def test_stale_removal_projects_only_when_clean_is_requested(self) -> None:
        with self.prepare() as temporary:
            root = Path(temporary)
            write_skill(root, "beta")
            self.assertEqual(run_quiet(["--repo-root", str(root)])[0], 0)
            shutil.rmtree(root / "agent-plugins" / "skills" / "beta")

            with_clean = generator.project_release(root, clean=True)
            without_clean = generator.project_release(root, clean=False)
            self.assertTrue(all(item.bump == "minor" for item in with_clean))
            self.assertTrue(all(item.bump is None for item in without_clean))
            self.assertEqual(
                self.projected_versions(root, clean=True),
                self.real_run_versions(root, "--clean"),
            )
            self.assertEqual(
                self.projected_versions(root, clean=False),
                self.real_run_versions(root),
            )

    def test_dry_run_prints_the_projection_and_writes_nothing(self) -> None:
        with self.prepare() as temporary:
            root = Path(temporary)
            before = tree_digest(root)
            code, output = run_quiet(["--repo-root", str(root), "--dry-run"])
            self.assertEqual(code, 0)
            self.assertIn(
                "Projected version: claude major 1.2.3 -> 2.0.0; "
                "codex major 1.2.3 -> 2.0.0.",
                output,
            )
            self.assertEqual(tree_digest(root), before)
            self.assertFalse((root / "claude").exists())

    def test_dry_run_matches_the_standalone_projection(self) -> None:
        with self.prepare() as temporary:
            root = Path(temporary)
            code, output = run_quiet(["--repo-root", str(root), "--dry-run", "--clean"])
            self.assertEqual(code, 0)
            expected = generator.format_version_projection(
                generator.project_release(root, clean=True)
            )
            self.assertIn(expected, output)

    def test_dry_run_notes_that_no_version_bump_suppresses_the_increment(self) -> None:
        with self.prepare() as temporary:
            root = Path(temporary)
            _code, output = run_quiet(
                ["--repo-root", str(root), "--dry-run", "--no-version-bump"]
            )
            self.assertIn("--no-version-bump would suppress the increment.", output)

    def test_dry_run_of_a_current_tree_reports_no_change(self) -> None:
        with self.prepare() as temporary:
            root = Path(temporary)
            self.assertEqual(run_quiet(["--repo-root", str(root)])[0], 0)
            _code, output = run_quiet(["--repo-root", str(root), "--dry-run"])
            self.assertIn("Projected version: claude unchanged; codex unchanged.", output)

    def test_dry_run_without_manifests_still_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "alpha")
            code, output = run_quiet(["--repo-root", str(root), "--dry-run"])
            self.assertEqual(code, 0)
            self.assertIn("unavailable", output)

    def test_projection_covers_a_single_platform(self) -> None:
        with self.prepare() as temporary:
            root = Path(temporary)
            projections = generator.project_release(root, platform="codex")
            self.assertEqual([item.platform for item in projections], ["codex"])


class RemovedSkillNotesTests(unittest.TestCase):
    def test_removed_skills_are_detected_from_skill_file_deletions_only(self) -> None:
        changes = [
            ("D", "agent-plugins/skills/stop-slop/SKILL.md"),
            ("D", "agent-plugins/skills/stop-slop/references/phrases.md"),
            ("M", "agent-plugins/skills/code-review/SKILL.md"),
            ("D", "agent-plugins/skills/old/references/SKILL.md"),
        ]
        self.assertEqual(release_notes.removed_skills(changes), ["stop-slop"])

    def test_release_notes_name_the_removal_and_the_replacements(self) -> None:
        changes = [
            ("D", "agent-plugins/skills/stop-slop/SKILL.md"),
            ("D", "claude/skills/stop-slop/SKILL.md"),
            ("M", "README.md"),
        ]
        with (
            mock.patch.object(release_notes, "previous_release_tag", return_value="v29.2.0"),
            mock.patch.object(release_notes, "changed_files", return_value=changes),
        ):
            notes = release_notes.render_notes("all", "30.0.0", "HEAD")
        self.assertIn("Removed skills:", notes)
        self.assertIn("`stop-slop`", notes)
        self.assertIn("`ai-detector` for prose analysis", notes)
        self.assertIn("`humanizer` for edits", notes)

    def test_an_unrecorded_removal_still_gets_a_line(self) -> None:
        changes = [("D", "agent-plugins/skills/gone/SKILL.md")]
        with (
            mock.patch.object(release_notes, "previous_release_tag", return_value=None),
            mock.patch.object(release_notes, "changed_files", return_value=changes),
        ):
            notes = release_notes.render_notes("all", "30.0.0", "HEAD")
        self.assertIn("- `gone`: No replacement is recorded.", notes)


if __name__ == "__main__":
    unittest.main()
