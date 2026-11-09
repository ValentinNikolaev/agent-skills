from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "agent-plugins" / "shared" / "memory" / "validate_memory.py"
TODAY = "2026-08-08"

_spec = importlib.util.spec_from_file_location("validate_memory_under_test", VALIDATOR)
validate_memory = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = validate_memory
_spec.loader.exec_module(validate_memory)


def write_memory(root: Path, number: int) -> str:
    name = f"topic-{chr(ord('a') + number // 26)}{chr(ord('a') + number % 26)}"
    (root / f"{name}.md").write_text(
        "---\n"
        "memory_contract: 1\n"
        f"name: {name}\n"
        f"description: Fixture memory number {number} with unique wording.\n"
        "type: project\n"
        "related: []\n"
        "provenance:\n"
        "  - kind: repository\n"
        "    locator: .\n"
        f"    retrieved_at: {TODAY}\n"
        "    revision: fixture\n"
        f"last_updated: {TODAY}\n"
        f"last_reviewed: {TODAY}\n"
        "---\n\n"
        f"# Topic {number}\n\nFixture fact {number}.\n",
        encoding="utf-8",
    )
    return (
        f"- [{name}.md]({name}.md) — project — Fixture purpose number {number}\n"
    )


def build_store(root: Path, files: int, newline: str = "\n") -> None:
    entries = [write_memory(root, number) for number in range(files)]
    text = "# Memory\n\n" + "".join(entries)
    (root / "MEMORY.md").write_bytes(
        text.replace("\n", newline).encode("utf-8")
    )


def validate(root: Path, *options: str) -> tuple[int, dict]:
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        code = validate_memory.main(
            [str(root), "--today", TODAY, "--format", "json", *options]
        )
    return code, json.loads(output.getvalue())


def capacity(payload: dict) -> list[tuple[str, str, str]]:
    return [
        (item["code"], item["severity"], item["message"])
        for item in payload["findings"]
        if item["code"].startswith("CAPACITY_")
    ]


class MemoryCapacityTests(unittest.TestCase):
    def test_defaults_follow_the_documented_host_window(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_store(root, 1)
            _code, payload = validate(root)
        configuration = payload["configuration"]
        self.assertEqual(configuration["file_limit"], 200)
        self.assertEqual(configuration["index_line_limit"], 200)
        self.assertEqual(configuration["index_byte_limit"], 25000)
        self.assertFalse(configuration["enforce_limits"])

    def test_one_hundred_file_store_is_not_capacity_critical(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_store(root, 100)
            code, payload = validate(root)
        self.assertEqual(code, 0)
        self.assertEqual(payload["summary"]["files"], 100)
        self.assertEqual(capacity(payload), [])

    def test_index_line_limit_binds_no_later_than_the_file_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_store(root, 200)
            _code, payload = validate(root)
        metrics = {message.split(" capacity")[0] for _c, _s, message in capacity(payload)}
        self.assertEqual(metrics, {"file count", "index lines"})
        self.assertGreaterEqual(
            payload["summary"]["index_lines"], payload["summary"]["files"]
        )

    def test_each_limit_is_advisory_at_warning_and_critical_ratios(self) -> None:
        cases = {
            "file-limit": ("file count", ".", 4),
            "index-line-limit": ("index lines", "MEMORY.md", 5),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_store(root, 3)
            size = payload_bytes(root)
            for option, (metric, path, limit) in cases.items():
                with self.subTest(option=option, ratio="warning"):
                    code, payload = validate(root, f"--{option}", str(limit))
                    self.assertEqual(code, 0)
                    found = capacity(payload)
                    self.assertEqual(len(found), 1)
                    self.assertEqual(found[0][:2], ("CAPACITY_WARNING", "info"))
                    self.assertIn(metric, found[0][2])
                    self.assertIn("advisory", found[0][2])
                    self.assertEqual(
                        [i["path"] for i in payload["findings"] if i["code"].startswith("CAPACITY_")],
                        [path],
                    )
            with self.subTest(option="index-byte-limit", ratio="warning"):
                code, payload = validate(
                    root, "--index-byte-limit", str(int(size / 0.8))
                )
                self.assertEqual(code, 0)
                found = capacity(payload)
                self.assertEqual(found[0][:2], ("CAPACITY_WARNING", "info"))
                self.assertIn("index bytes", found[0][2])
            for option, limit in (
                ("file-limit", 3),
                ("index-line-limit", 4),
                ("index-byte-limit", size),
            ):
                with self.subTest(option=option, ratio="critical"):
                    code, payload = validate(root, f"--{option}", str(limit))
                    self.assertEqual(code, 0)
                    found = capacity(payload)
                    self.assertEqual(len(found), 1)
                    self.assertEqual(found[0][:2], ("CAPACITY_CRITICAL", "info"))

    def test_enforced_limits_raise_severity_and_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_store(root, 3)
            size = payload_bytes(root)
            for option, warn, crit in (
                ("file-limit", 4, 3),
                ("index-line-limit", 5, 4),
                ("index-byte-limit", int(size / 0.8), size),
            ):
                with self.subTest(option=option, ratio="warning"):
                    code, payload = validate(
                        root, f"--{option}", str(warn), "--enforce-limits"
                    )
                    self.assertEqual(code, 1)
                    self.assertEqual(
                        capacity(payload)[0][:2], ("CAPACITY_WARNING", "warning")
                    )
                with self.subTest(option=option, ratio="critical"):
                    code, payload = validate(
                        root, f"--{option}", str(crit), "--enforce-limits"
                    )
                    self.assertEqual(code, 1)
                    self.assertEqual(
                        capacity(payload)[0][:2], ("CAPACITY_CRITICAL", "critical")
                    )

    def test_index_size_counts_stored_bytes_not_normalized_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_store(root, 2, newline="\r\n")
            stored = payload_bytes(root)
            _code, payload = validate(root)
            self.assertEqual(payload["summary"]["index_bytes"], stored)
            self.assertGreater(stored, len((root / "MEMORY.md").read_text(encoding="utf-8")))

    def test_missing_index_reports_no_capacity_use(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_memory(root, 0)
            _code, payload = validate(root)
        self.assertEqual(payload["summary"]["index_bytes"], 0)
        self.assertEqual(payload["summary"]["index_lines"], 0)

    def test_non_positive_limits_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_store(root, 1)
            for option in ("--file-limit", "--index-line-limit", "--index-byte-limit"):
                with self.subTest(option=option):
                    result = subprocess.run(
                        [sys.executable, str(VALIDATOR), str(root), option, "0"],
                        check=False,
                        capture_output=True,
                        encoding="utf-8",
                    )
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("capacity limits", result.stderr)

    def test_text_report_shows_index_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build_store(root, 1)
            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(root), "--today", TODAY],
                check=False,
                capture_output=True,
                encoding="utf-8",
            )
        self.assertIn("index bytes: ", result.stdout)


def payload_bytes(root: Path) -> int:
    return len((root / "MEMORY.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
