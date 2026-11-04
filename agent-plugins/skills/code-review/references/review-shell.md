# Shell and Make review

Read this reference when a diff changes Makefiles, shell scripts, hook commands, or CI steps, including shell embedded in JSON/YAML. Review the executed commands and their callers; a formatter or development hook can execute untrusted repository filenames. Keep the parent skill's scope, evidence, and verification rules.

## Trace data through each parser

Identify the actual interpreter, Make `SHELL` and recipe boundaries, shell flags, working directory, and wrapper (`sh -c`, hook runner, CI runner). Trace filename discovery through Make expansion, shell parsing, argument construction, and the invoked tool. A variable containing a fixed command fragment is different from one containing command output or filenames.

- Flag command output inserted into recipe/script source: `$(shell ...)` in recipes, a Make variable backed by it, generated scripts, `eval`, or interpolated `sh -c` strings. Make expands before the shell parses: `files="$(changed_go_files)"` is unsafe when the Make variable contains arbitrary filenames, even inside double quotes. A filename containing `$(...)`, a backtick, or a quote can become shell syntax.
- Trace unquoted `$files`, Make's `$$files`, and `for f in $(...)` separately. Ordinary shell variable/command substitution does not recursively execute metacharacters in its output without another parser such as `eval`; it does perform word splitting and glob expansion when unquoted. Do not call every unquoted expansion command injection.
- Require filename data to stay data end to end: NUL-delimited discovery (`git diff -z --name-only`, `git ls-files -z`, `find -print0`) and NUL-aware consumers (`xargs -0`, or an array/read loop supported by the actual shell). Do not store a NUL stream in shell command substitution or a Make variable. Quoting a newline-separated list cannot recover lost filename boundaries.
- Keep filters, deduplication, and directory extraction filename-safe too. A pipeline that starts with `git -z` but uses newline-based `sort`, `sed`, or `dirname` output before converting newlines back to NUL is still lossy. Check the actual platform's support for NUL-aware options.
- Pass arguments into `sh -c` as positional parameters with a dummy `$0`, then forward quoted `"$@"`; use `"$$@"` in Make recipes so the shell receives `"$@"`. Never embed the discovered list in the script string. Account for empty input, batching, and option-like paths with `--` or a safe path prefix where the tool supports it.

For example, a shell pipeline can keep names outside the command string:

```sh
git ls-files -z --others --exclude-standard -- '*.go' |
  xargs -0 sh -c '[ "$#" -eq 0 ] || formatter -- "$@"' fmt-changed
```

This illustrates argument transport only; verify the formatter's actual options, file selection, and exit behavior. In a Make recipe, escape each shell dollar sign as `$$`. If using `xargs -r` to skip empty input, establish that the target implementation supports it.

## Check argument boundaries

Trace names containing spaces, tabs, newlines, glob characters, quotes, and command-substitution text to the final tool's argv. A normal `new file.go` must remain one argument. Check `$*`, unquoted `$@`, `for f in $files`, `for f in $(find ...)`, plain `xargs`, and space-separated Make lists used as arbitrary path lists. Quoted `"$files"` instead passes an entire multi-file list as one argument; quoted `"$@"` preserves separate arguments.

Use bounded scratch probes with harmless marker names and an argv-recording stub instead of running project hooks or downloaded tools. Compare an unsafe form with a filename-safe control. Keep injection, splitting, selection errors, and tool option parsing distinct; one safe transport stage does not prove the whole pipeline safe.

## Check partial failures and unrelated work

For `tool_a "$@" && tool_b "$@" && tool_c "$@"`, trace a failure on one input in a batch. Does it suppress formatting, checks, or cleanup for unrelated files? Check per-file chains and separate recipe lines too: Make normally stops a target at the first failed recipe, and `set -e` can stop a script even after `&&` is removed.

Establish the intended contract before flagging. Fail-fast is correct when later work requires the failed output. It is a candidate when independent tools/files must still run and one bad file prevents that work. Name the failed tool/input and the skipped unrelated work. A repair must both attempt required independent work and preserve an aggregate failure status; replacing `&&` with `;` or adding `|| true` alone can hide failures. Probe with a stub that fails for one input and records every attempted tool/file pair.

## Verify line endings with the executed shell

When a changed executable script may be checked out under `core.autocrlf`, inspect `.gitattributes`, `git check-attr text eol`, `git config --show-origin --get core.autocrlf`, and `git ls-files --eol` for that path. Distinguish committed blob bytes from checkout bytes and direct shebang execution from `bash script` or sourcing. Identify the interpreter actually used by the hook/CI runner, including version/build and relevant options.

Before flagging a CRLF execution defect, reproduce the affected syntax in an isolated LF/CRLF pair using that actual shell and invocation. Record exit status and output; use a harmless fixture or stub external effects. Git for Windows Bash, WSL Bash, and other builds may behave differently. Neither `core.autocrlf=true` nor a CRLF byte sequence alone proves a runtime failure. If the supported interpreter is unavailable, record the verification limit and required check rather than asserting a CRLF defect. If it accepts the CRLF control, refute that scenario; an `eol=lf` preference alone is not a correctness finding.

## Evidence behind these checks

Copilot identified filename interpolation in `fmt-changed` in [support-automation-ai #439](https://github.com/simple-life-app/support-automation-ai/pull/439), [support-automation #785](https://github.com/simple-life-app/support-automation/pull/785), and [med-support #213](https://github.com/Simple-Life-Medical/med-support/pull/213). Author replies confirmed fixes using NUL-delimited Git output and paths containing spaces and command-substitution text. The CRLF claim on #439 was later corrected after the author's Git for Windows Bash accepted a CRLF copy. These are evidence for the mechanisms above, not universal project conventions. The user reported that a standard-depth review at head `e801da2` missed the filename injection; this motivates both shell routing and the coordinator's mandatory reference-read gate, without claiming measured recall.
