from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import generate_skill_wrappers as generator  # noqa: E402

RENAMES = {
    "create-github-pages": "github-pages-create",
    "improve-github-pages": "github-pages-improve",
    "audit-github-pages-ux": "github-pages-audit",
    "github-pages-content-architecture": "github-pages-content",
    "github-pages-visual-system": "github-pages-design",
}


class PagesMigrationTests(unittest.TestCase):
    def test_family_upgrade_preserves_manual_work_and_resolves_links(self):
        with tempfile.TemporaryDirectory(prefix="pages-migration-") as temporary:
            root = Path(temporary).resolve()
            source = root / "agent-plugins" / "skills"
            for old in RENAMES:
                folder = source / old
                folder.mkdir(parents=True)
                (folder / "SKILL.md").write_text(
                    f"---\nname: {old}\ndescription: Legacy Pages migration fixture.\n"
                    "---\n\n# Legacy fixture\n", encoding="utf-8",
                )
            for platform in ("codex", "claude"):
                manifest = root / f".{platform}-plugin" / "plugin.json"
                manifest.parent.mkdir()
                manifest.write_text(
                    json.dumps({"name": "fixture", "version": "1.2.3"}), encoding="utf-8",
                )
            output = io.StringIO()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                self.assertEqual(generator.run([
                    "--repo-root", str(root), "--no-version-bump", "--quiet"
                ]), 0, output.getvalue())
            manual = {}
            for platform in ("codex", "claude"):
                path = root / platform / "skills" / "personal-pages" / "SKILL.md"
                path.parent.mkdir()
                path.write_bytes(b"# Locally authored skill\nDo not replace.\n")
                manual[path] = path.read_bytes()
            for old, new in RENAMES.items():
                obsolete = (source / old).resolve()
                self.assertEqual(obsolete.parent, source.resolve())
                shutil.rmtree(obsolete)
                shutil.copytree(REPO_ROOT / "agent-plugins" / "skills" / new, source / new)
            migration = root / "docs" / "github-pages-family-migration.md"
            migration.parent.mkdir()
            shutil.copyfile(REPO_ROOT / "docs" / migration.name, migration)
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                self.assertEqual(generator.run([
                    "--repo-root", str(root), "--clean", "--strict-links", "--quiet"
                ]), 0, output.getvalue())
                self.assertEqual(generator.run([
                    "--repo-root", str(root), "--check", "--clean",
                    "--strict-links", "--quiet"
                ]), 0, output.getvalue())
            for path, original in manual.items():
                self.assertEqual(path.read_bytes(), original)
            for platform in ("codex", "claude"):
                manifest = root / f".{platform}-plugin" / "plugin.json"
                version = json.loads(manifest.read_text())["version"]
                self.assertTrue(version.startswith(f"2.0.0+{platform}."), version)
                for old, new in RENAMES.items():
                    self.assertFalse((root / platform / "skills" / old).exists())
                    package = root / platform / "skills" / new
                    self.assertEqual(generator.validate_local_links(
                        generator.read_source_skill(package)
                    ), [])
                    metadata = (package / "agents" / "openai.yaml").read_text(encoding="utf-8")
                    self.assertIn(f"${new}", metadata)
                    self.assertIn('display_name: "GitHub Pages:', metadata)
                design = root / platform / "skills" / "github-pages-design"
                for license_file in (source / "github-pages-design").glob("LICENSE.*"):
                    self.assertEqual(
                        (design / license_file.name).read_bytes(),
                        license_file.read_bytes().replace(b"\r\n", b"\n"),
                    )
            readme = (root / "README.md").read_text(encoding="utf-8")
            for old, new in RENAMES.items():
                self.assertIn(f"agent-plugins/skills/{new}/SKILL.md", readme)
                self.assertNotIn(f"agent-plugins/skills/{old}/SKILL.md", readme)
            self.assertIn("docs/github-pages-family-migration.md", readme)

            # Negative control: missing owner reference must fail strict links.
            handoff = source / "github-pages-create" / "references" / "workflow-handoffs.md"
            handoff.unlink()
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                self.assertEqual(generator.run([
                    "--repo-root", str(root), "--check", "--clean",
                    "--strict-links", "--quiet"
                ]), 1)
            self.assertIn("workflow-handoffs.md", output.getvalue())


if __name__ == "__main__":
    unittest.main()
