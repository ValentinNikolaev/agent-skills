"""Exercise repository-owned shell/Make controls, not model review accuracy.

All commands and marker files stay in disposable directories. No project hooks,
formatters, downloaded scripts, or external PR code execute.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


def shell_path():
    if os.name == "nt":
        git_bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
        return str(git_bash) if git_bash.is_file() else None
    return shutil.which("bash")


BASH = shell_path()
MAKE = shutil.which("make")
GIT = shutil.which("git")


@unittest.skipUnless(BASH, "Bash required for executable shell review controls")
class ShellReviewExamples(unittest.TestCase):
    def run_shell(self, script, root):
        return subprocess.run(
            [BASH, "--noprofile", "--norc", "-c", script], cwd=root,
            capture_output=True, timeout=15, check=False,
        )

    def write_script(self, root, name, source):
        (root / name).write_bytes(source.encode("utf-8"))

    @unittest.skipUnless(MAKE and GIT, "Git and Make required for recipe controls")
    def test_make_interpolation_executes_filename_but_nul_arguments_preserve_it(self):
        names = ["plain.go", "new file.go", "$(touch${IFS}INJECTED).go", "[glob].go"]
        if os.name != "nt":
            names.append("new\nline.go")
        for safe in (False, True):
            with self.subTest(safe=safe), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                initialized = subprocess.run(
                    [GIT, "-c", "init.templateDir=", "init", "-q", "."], cwd=root,
                    capture_output=True, timeout=10, check=False,
                )
                self.assertEqual(initialized.returncode, 0, initialized.stderr)
                for name in names:
                    (root / name).write_bytes(b"package probe\n")
                self.write_script(root, "argv.sh", 'printf \'%s\\0\' "$@" >> argv.bin\n')
                recipe = (
                    "\t@git ls-files -z --others --exclude-standard -- '*.go' | "
                    "xargs -0 sh -c 'sh ./argv.sh \"$$@\"' fmt-changed\n"
                    if safe else
                    '\t@files="$(shell git ls-files --others --exclude-standard -- \'*.go\')"; '
                    'sh ./argv.sh $$files\n'
                )
                self.write_script(root, "probe.mk", "fmt-changed:\n" + recipe)
                result = subprocess.run(
                    [MAKE, "--no-print-directory", "-f", "probe.mk", f"SHELL={Path(BASH).as_posix()}"],
                    cwd=root, capture_output=True, timeout=15, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                argv = (root / "argv.bin").read_bytes().split(b"\0")[:-1]
                if safe:
                    self.assertFalse((root / "INJECTED").exists())
                    self.assertCountEqual(argv, [name.encode("utf-8") for name in names])
                else:
                    self.assertTrue((root / "INJECTED").exists())
                    self.assertNotIn(b"new file.go", argv)
                    self.assertIn(b"new", argv)

    def test_shell_expansion_splits_but_does_not_reparse_command_substitution(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            script = (
                "files='$(touch${IFS}INJECTED).go new file.go'\n"
                'set -- $files\nprintf \'%s\\0\' "$@"\n'
            )
            result = self.run_shell(script, root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((root / "INJECTED").exists())
            self.assertEqual(
                result.stdout.split(b"\0")[:-1],
                [b"$(touch${IFS}INJECTED).go", b"new", b"file.go"],
            )

    def test_independent_work_runs_after_failure_and_failure_status_survives(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = (
                'tool_a() { printf \'a:%s\\n\' "$@"; return 1; }\n'
                'tool_b() { printf \'b:%s\\n\' "$@"; }\n'
                'set -- bad.go unrelated.go\n'
            )
            chained = self.run_shell(tools + 'tool_a "$@" && tool_b "$@"\n', root)
            aggregated = self.run_shell(
                tools + 'status=0\ntool_a "$@" || status=$?\n'
                'tool_b "$@" || status=$?\nexit "$status"\n', root,
            )
            self.assertNotEqual(chained.returncode, 0)
            self.assertNotIn(b"b:unrelated.go", chained.stdout)
            self.assertNotEqual(aggregated.returncode, 0)
            self.assertIn(b"b:unrelated.go", aggregated.stdout)

    def test_lf_crlf_probe_uses_observed_shell_behavior(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = b'set -u\nfile=probe.go\ncase "$file" in\n  *.go) printf "OK\\n" ;;\nesac\n'
            results = []
            for name, content in (("lf.sh", source), ("crlf.sh", source.replace(b"\n", b"\r\n"))):
                (root / name).write_bytes(content)
                results.append(subprocess.run(
                    [BASH, "--noprofile", "--norc", name], cwd=root,
                    capture_output=True, timeout=10, check=False,
                ))
            lf, crlf = results
            self.assertEqual((lf.returncode, lf.stdout), (0, b"OK\n"), lf.stderr)
            # Accept either result: shell builds differ. A failed CRLF control
            # needs observed diagnostics; a successful one must do the work.
            if crlf.returncode:
                self.assertTrue(crlf.stderr)
            else:
                self.assertEqual(crlf.stdout, lf.stdout)


if __name__ == "__main__":
    unittest.main()
