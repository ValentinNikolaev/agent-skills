"""Check rewritten examples, not model routing or general skill effectiveness.

Compiler/runtime checks use already-installed tools from SKILL_TYPESCRIPT_MODULES.
They never download packages or execute upstream scripts. Missing tools are skips.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "agent-plugins" / "skills"
FIXTURES = ROOT / "tests" / "fixtures" / "typescript_zod_examples.json"


def examples():
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def example_source(case):
    path = SKILLS / case["skill"] / case["reference"]
    blocks = re.findall(r"```typescript\n(.*?)\n```", path.read_text(encoding="utf-8"), re.S)
    if len(blocks) != 1:
        raise AssertionError(f"{path}: expected one complete executable example")
    return blocks[0] + "\n"


class ExampleStructureTests(unittest.TestCase):
    def test_examples_reference_real_packages_and_independent_observations(self):
        cases = examples()
        self.assertEqual({case["skill"] for case in cases}, {"zod", "typescript-type-design"})
        self.assertEqual(len({case["id"] for case in cases}), len(cases))
        for case in cases:
            with self.subTest(case=case["id"]):
                source = example_source(case)
                self.assertIn("export ", source)
                self.assertIn("assert.", case["runtime_assertions"])
                control = case.get("runtime_negative_control")
                if control:
                    self.assertEqual(source.count(control["original"]), 1)
                    self.assertIn(control["expected_failure"], case["runtime_assertions"])


class ExecutableExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module_path = os.environ.get("SKILL_TYPESCRIPT_MODULES")
        cls.node = shutil.which("node")
        if not module_path or not cls.node:
            raise unittest.SkipTest("Set SKILL_TYPESCRIPT_MODULES to installed TypeScript 5.5+ and Zod 4.4.3 modules; no packages were installed")
        cls.modules = Path(module_path).resolve()
        cls.compiler = cls.modules / "typescript" / "lib" / "tsc.js"
        if not cls.compiler.is_file() or not (cls.modules / "zod" / "package.json").is_file():
            raise unittest.SkipTest("Configured TypeScript/Zod modules are unavailable")
        cls.environment = os.environ.copy()
        cls.environment["NODE_PATH"] = str(cls.modules)
        cls.versions = {
            name: json.loads((cls.modules / name / "package.json").read_text(encoding="utf-8"))["version"]
            for name in ("typescript", "zod")
        }

    def compile(self, directory, source):
        (directory / "example.ts").write_text(source, encoding="utf-8")
        config = {
            "compilerOptions": {
                "target": "ES2022", "module": "CommonJS", "moduleResolution": "Node",
                "strict": True, "noUncheckedIndexedAccess": True,
                "exactOptionalPropertyTypes": True, "esModuleInterop": True,
                "noEmitOnError": True, "outDir": "out", "lib": ["ES2022"],
                "paths": {"zod": [str(self.modules / "zod")]},
            },
            "files": ["example.ts"],
        }
        (directory / "tsconfig.json").write_text(json.dumps(config), encoding="utf-8")
        return subprocess.run(
            [self.node, str(self.compiler), "--project", str(directory / "tsconfig.json"), "--pretty", "false"],
            cwd=directory, env=self.environment, capture_output=True, text=True, check=False, timeout=30,
        )

    def runtime(self, directory, case):
        harness = (
            "const assert = require('node:assert/strict');\n"
            "const subject = require('./out/example.js');\n"
            "async function main() {\n" + case["runtime_assertions"] + "\n"
            + "process.stdout.write(" + json.dumps(case["expected_stdout"]) + ");\n}\n"
            "main().catch(error => { console.error(error); process.exitCode = 1; });\n"
        )
        (directory / "probe.cjs").write_text(harness, encoding="utf-8")
        return subprocess.run(
            [self.node, str(directory / "probe.cjs")], cwd=directory, env=self.environment,
            capture_output=True, text=True, check=False, timeout=15,
        )

    def test_type_examples_enforce_accepted_and_rejected_calls(self):
        case = next(case for case in examples() if case["skill"] == "typescript-type-design")
        source = example_source(case)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            positive = self.compile(directory, source)
            self.assertEqual(positive.returncode, 0, str(self.versions) + positive.stdout + positive.stderr)
            runtime = self.runtime(directory, case)
            self.assertEqual(runtime.returncode, 0, runtime.stderr)
            self.assertEqual(runtime.stdout, case["expected_stdout"])
            self.assertEqual(source.count("@ts-expect-error"), 2)
            negative = self.compile(directory, re.sub(r"^// @ts-expect-error[^\n]*\n", "", source, flags=re.M))
            self.assertNotEqual(negative.returncode, 0)
            self.assertIn("TS2344", negative.stdout, "the false equality must violate its constraint")
            self.assertIn("TS2345", negative.stdout, "the mismatched payload must be rejected")
            unused = self.compile(directory, source.replace('describeEvent("saved", { count: 2 });', 'describeEvent("saved", { id: "a" });'))
            self.assertNotEqual(unused.returncode, 0)
            self.assertIn("TS2578", unused.stdout, "a now-valid call must expose its unused suppression")

    def test_zod_examples_validate_runtime_contract_and_negative_control(self):
        self.assertEqual(self.versions["zod"], "4.4.3", "fixture verification is pinned; explicitly evaluate other versions")
        case = next(case for case in examples() if case["skill"] == "zod")
        source = example_source(case)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            compiled = self.compile(directory, source)
            self.assertEqual(compiled.returncode, 0, str(self.versions) + compiled.stdout + compiled.stderr)
            positive = self.runtime(directory, case)
            self.assertEqual(positive.returncode, 0, positive.stderr)
            self.assertEqual(positive.stdout, case["expected_stdout"])
            control = case["runtime_negative_control"]
            changed = self.compile(directory, source.replace(control["original"], control["replacement"]))
            self.assertEqual(changed.returncode, 0, changed.stdout + changed.stderr)
            negative = self.runtime(directory, case)
            self.assertNotEqual(negative.returncode, 0)
            self.assertIn(control["expected_failure"], negative.stderr)
            restored = self.compile(directory, source)
            self.assertEqual(restored.returncode, 0, restored.stdout + restored.stderr)
            fixed = self.runtime(directory, case)
            self.assertEqual(fixed.returncode, 0, fixed.stderr)
            self.assertEqual(fixed.stdout, case["expected_stdout"])


if __name__ == "__main__":
    unittest.main()
