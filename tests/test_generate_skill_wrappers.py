from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import build_release_notes as release_notes  # noqa: E402
import generate_skill_wrappers as generator  # noqa: E402


class GeneratorRegressionTests(unittest.TestCase):
    def write_skill(
        self,
        root: Path,
        name: str,
        description: str,
        source_dir: Path = Path("agent-plugins/skills"),
    ) -> None:
        skill_dir = root / source_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n",
            encoding="utf-8",
        )

    def write_manifest(self, root: Path, platform: str, version: str) -> None:
        manifest_dir = root / f".{platform}-plugin"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        (manifest_dir / "plugin.json").write_text(
            json.dumps({"name": "fixture", "version": version}) + "\n",
            encoding="utf-8",
        )

    def test_targeted_generation_preserves_full_readme_catalog_and_versions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_skill(root, "alpha", "Use for alpha fixture work and validation.")
            self.write_skill(root, "beta", "Use for beta fixture work and validation.")
            self.write_manifest(root, "claude", "1.2.3")
            self.write_manifest(root, "codex", "1.2.3+local.7")

            result = generator.run(
                [
                    "--repo-root",
                    str(root),
                    "--no-version-bump",
                    "alpha",
                ]
            )

            self.assertEqual(result, 0)
            readme = (root / "README.md").read_text(encoding="utf-8")
            self.assertIn("`alpha`", readme)
            self.assertIn("`beta`", readme)
            self.assertTrue((root / "claude" / "skills" / "alpha" / "SKILL.md").is_file())
            self.assertFalse((root / "claude" / "skills" / "beta").exists())
            self.assertEqual(
                json.loads(
                    (root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
                )["version"],
                "1.2.3+local.7",
            )
            self.assertEqual(
                generator.run(["--repo-root", str(root), "--check", "alpha"]), 0
            )

    def test_version_contract_preserves_build_metadata_and_normalizes_releases(self) -> None:
        manifest = Path("plugin.json")
        self.assertEqual(
            generator.bump_version("2.4.9+cache.8", "minor", manifest),
            "2.5.0+cache.8",
        )
        self.assertEqual(
            generator.bump_version("2.4.9+cache.8", "major", manifest),
            "3.0.0+cache.8",
        )
        self.assertEqual(
            generator.combined_release_version(
                "8.0.0+claude.20260806141509",
                "8.0.0+codex.20260806141509",
            ),
            "8.0.0",
        )
        with self.assertRaises(generator.GenerationError):
            generator.bump_version("2.4.9-rc.1", "minor", manifest)
        with self.assertRaises(generator.GenerationError):
            generator.combined_release_version("8.0.0", "8.1.0+codex.1")

    def test_manifest_bumps_refresh_vendor_timestamp_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_manifest(root, "claude", "2.4.9+claude.20260101000000")
            platform = generator.PlatformTarget(
                key="claude",
                label="Claude",
                root=root / "claude" / "skills",
            )

            version = generator.bump_plugin_manifest(
                root,
                platform,
                "minor",
                "20260808165924",
            )

            self.assertEqual(version, "2.5.0+claude.20260808165924")
            manifest = json.loads(
                (root / ".claude-plugin" / "plugin.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["version"], version)
            with self.assertRaises(generator.GenerationError):
                generator.bump_plugin_manifest(root, platform, "minor", "20260808")

    def test_link_validation_ignores_code_examples(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_dir = Path(temporary) / "fixture"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: fixture\n"
                "description: Validate Markdown links in prose only.\n"
                "---\n\n"
                "`[inline](inline-missing.md)`\n\n"
                "```markdown\n[fenced](fenced-missing.md)\n```\n\n"
                "[real](real-missing.md)\n",
                encoding="utf-8",
            )
            skill = generator.read_source_skill(skill_dir)
            warnings = generator.validate_local_links(skill)
            self.assertEqual(len(warnings), 1)
            self.assertIn("real-missing.md", warnings[0])

    def test_release_workflows_share_the_generator_version_contract(self) -> None:
        for relative in (
            Path(".github/workflows/regenerate-skills.yml"),
            Path(".github/workflows/manual-release.yml"),
        ):
            with self.subTest(workflow=relative):
                text = (REPO_ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("from generate_skill_wrappers import", text)
                self.assertIn("combined_release_version", text)
        regenerate = (
            REPO_ROOT / ".github/workflows/regenerate-skills.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("version_core", regenerate)
        manual = (REPO_ROOT / ".github/workflows/manual-release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("git rev-parse HEAD", manual)
        self.assertIn("steps.release_target.outputs.sha", manual)
        self.assertIn(".workflow-tools/scripts", manual)
        self.assertNotIn("TARGET: ${{ github.sha }}", manual)

    def test_release_workflow_uses_master_push_and_plain_version_tags(self) -> None:
        regenerate = (
            REPO_ROOT / ".github/workflows/regenerate-skills.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("  push:\n", regenerate)
        self.assertIn("    branches:\n      - master\n", regenerate)
        self.assertIn("  group: regenerate-skills-master\n", regenerate)
        self.assertIn("  cancel-in-progress: false\n", regenerate)
        self.assertIn("EVENT_BEFORE: ${{ github.event.before }}", regenerate)
        self.assertIn("CURRENT_SHA: ${{ github.sha }}", regenerate)
        self.assertNotIn("pull_request_target", regenerate)
        self.assertNotIn("github.event.pull_request", regenerate)
        self.assertIn('tag="v${VERSION}"', regenerate)
        self.assertIn('--title "$tag"', regenerate)
        self.assertNotIn('tag="agent-plugins-v${VERSION}"', regenerate)

        manual = (REPO_ROOT / ".github/workflows/manual-release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("        default: master\n", manual)
        self.assertIn('tag = f"v{version}"', manual)
        self.assertIn('tag="v${VERSION}"', manual)
        self.assertIn('--title "$tag"', manual)
        self.assertIn('"agent-plugins-v*"', manual)
        self.assertNotIn('tag="agent-plugins-v${VERSION}"', manual)

    def test_combined_release_notes_accept_new_and_legacy_tag_history(self) -> None:
        with mock.patch.object(
            release_notes, "run_git", return_value="v9.0.0"
        ) as run_git:
            self.assertEqual(
                release_notes.previous_release_tag("all", "HEAD"), "v9.0.0"
            )

        run_git.assert_called_once_with(
            [
                "describe",
                "--tags",
                "--match",
                "v*",
                "--match",
                "agent-plugins-v*",
                "--abbrev=0",
                "HEAD^",
            ],
            check=False,
        )

    def test_shared_memory_validator_is_injected_into_standalone_packages(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.write_skill(
                root,
                "audit-memory",
                "Audit memory fixtures with the centrally maintained validator.",
            )
            shared = root / "agent-plugins" / "shared" / "memory"
            shared.mkdir(parents=True)
            validator = "#!/usr/bin/env python3\nprint('shared fixture')\n"
            (shared / "validate_memory.py").write_text(validator, encoding="utf-8")
            self.write_manifest(root, "claude", "1.2.3")
            self.write_manifest(root, "codex", "1.2.3")

            result = generator.run(
                [
                    "--repo-root",
                    str(root),
                    "--no-version-bump",
                    "audit-memory",
                ]
            )

            self.assertEqual(result, 0)
            for platform in ("claude", "codex"):
                generated = (
                    root
                    / platform
                    / "skills"
                    / "audit-memory"
                    / "scripts"
                    / "validate_memory.py"
                )
                self.assertEqual(generated.read_text(encoding="utf-8"), validator)

    def test_custom_shared_directory_is_independent_of_source_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir = Path("custom/skills")
            shared_dir = Path("common/resources")
            self.write_skill(
                root,
                "audit-memory",
                "Audit memory fixtures with a configurable shared-resource root.",
                source_dir,
            )
            shared = root / shared_dir / "memory"
            shared.mkdir(parents=True)
            validator = "#!/usr/bin/env python3\nprint('custom shared fixture')\n"
            (shared / "validate_memory.py").write_text(validator, encoding="utf-8")
            self.write_manifest(root, "claude", "1.2.3")
            self.write_manifest(root, "codex", "1.2.3")

            result = generator.run(
                [
                    "--repo-root",
                    str(root),
                    "--source-dir",
                    str(source_dir),
                    "--shared-dir",
                    str(shared_dir),
                    "--no-version-bump",
                    "audit-memory",
                ]
            )

            self.assertEqual(result, 0)
            generated = (
                root
                / "codex"
                / "skills"
                / "audit-memory"
                / "scripts"
                / "validate_memory.py"
            )
            self.assertEqual(generated.read_text(encoding="utf-8"), validator)


if __name__ == "__main__":
    unittest.main()
