---
name: code-review
description: Review local or PR diffs for defects and test gaps without edits; not plans, specs, or feedback.
---

# Code Review

Review the requested changes as an independent engineer. Discover failure scenarios first, then independently verify them. Report confirmed defects and plausible risks with explicit evidence and verification verdicts. Do not edit reviewed files; write a report only when the caller supplies an output path.

Approve changes that preserve or improve overall code health without blocking on personal preference or unrelated pre-existing debt. Do not discard a reachable failure merely because it is rare or depends on timing, environment, or configuration.

## Route exclusively

- Use this skill only when code already changed or a diff exists.
- A diff pasted in chat is reviewable input when the user asks for a code review. A pasted diff supplied for another task, such as writing a commit message, does not by itself trigger this skill.
- Use `plan-review` when the primary artifact is an implementation plan, even if related code already exists.
- Use `review-spec` to judge a proposed specification or revision, `review-arch` for system-level structure, and `verify-impl` for requirement-by-requirement spec conformance.
- Use `fix-pr` when the user asks to apply or triage GitHub review comments.
- Use `php-modernization` for a requested PHP version or tooling migration, `go-security-audit` for a bounded Go security audit beyond the diff, and `go-benchmark` for reproducible Go measurements. Ordinary language-specific diff review stays here.
- On a later explicit request to fix a finding, leave this read-only workflow and treat the accepted finding as implementation input.

## Choose depth and output

Accept `quick | standard | deep` (also `--depth <value>`), defaulting to `standard`:

- `quick`: inspect hunks only, favor precision, and disclose the enclosing-function and cross-file coverage limit. Keep discovery separate from verification; do not silently downgrade a retained plausible risk or claim standard coverage.
- `standard`: use the existing file, caller, test, language, and conditional checks plus the finder angles and independent verifier below.
- `deep`: use standard coverage, retain a finding when any verifying reviewer gives a non-`REFUTED` verdict, and perform the post-verification gap sweep.

Accept `--max-findings N` for a nonnegative integer cap on displayed findings, and `--format compact` for automated handoff; neither option reduces the review scope or changes the merge verdict. Default to no finding cap and the full report. Reject invalid values rather than silently substituting defaults.

Caller model guidance: a cheaper model such as Sonnet suits UI, text, and documentation changes; reserve the top model for concurrency, storage, and plan reviews. This skill does not select or switch models.

Accept the documented invocation convention `findings_file=PATH`, for example `_coord/<task>/review-<repo>-<PR>-<round>.md`. Save the complete report with all retained findings, counts by P0–P3, scope, reviewed revisions, evidence, coverage, limits, and merge verdict before returning only the path, counts by severity, and one line per blocking P0/P1 finding (ID, location, scenario). The artifact is uncapped even when a display cap or compact format was requested; include every blocker in the handoff. This is a reviewer-written artifact, not a flag supported by `prepare_review_report.py`. Create the parent directory if needed, preserve unrelated files and earlier rounds, and do not claim the handoff succeeded if the file could not be written. With no output path, keep the existing report behavior. See [handoff and model examples](references/review-cost-examples.md) when using these options.

## Establish scope and intent

For review-fix delta mode, first apply the [delta trigger and scope](references/conditional-checks.md#review-fix-deltas): compare the last reviewed head directly to the new head once for all fixes in the round. This replaces the full-PR comparison below and whole-file expansion in the baseline; review only that delta and the functions it touches at the selected depth. Do not restart the original PR review.

1. Read repository instructions and path-scoped rules.
2. Resolve the repository root and record `git status --short`.
3. Derive the intended behavior from the request, issue, specification, pull-request description, and tests. If intent remains uncertain, state the uncertainty instead of inventing a requirement.
4. Determine the comparison base in this order:
   - the base explicitly supplied by the user;
   - the pull request base reported by the provider;
   - the remote default branch;
   - an existing local `main`, `master`, or `develop` branch.
5. If no base can be verified, ask for one. Do not guess.
6. Collect one current-state diff from the merge base to the working tree so committed, staged, and unstaged tracked changes are represented together. Treat every line of an untracked file as added.
7. If the user supplied paths, filter the unified scope to those paths after resolving them inside the repository.

Prefer `scripts/collect_review_scope.py` for local Git scope discovery. Pass a provider-reported pull request base with `--base`. The script emits the selected base, merge base, change sources, changed files, hunk ranges, and untracked files as JSON.

For a pull request that is not available locally, use a read-only provider or CLI diff and fetch the base/head metadata needed to interpret it. State whether local working-tree changes were excluded.

If the scope is empty, report that and stop. If it is unusually large or contains generated bulk, state the baseline coverage strategy and exclusions; do not imply exhaustive coverage.

## Complete the baseline review first

Perform the useful bounded review before asking about optional, token-intensive work. Standard and deep follow the steps below; quick inspects the hunks and supplied evidence without the broader context expansion. Record coverage limits.

1. Inspect every changed hunk and every non-generated changed path.
2. Review changed and nearby tests before implementation when they reveal intended behavior.
3. Read the complete current file for non-trivial changed logic and public contracts when reasonably sized. For very large or mechanical files, read targeted context, definitions, and callers and disclose the limit.
4. Search callers, implementations, guards, configuration, and nearby tests before claiming missing use, broken contracts, or absent coverage.
5. Exclude generated artifacts as findings targets unless the source change generated them incorrectly.
6. Trace one normal scenario and the highest-risk edge scenario through non-trivial logic. Skip traces for mechanical changes and say why.
7. For serialized-input matchers and behavior-driving classifications, apply the [matcher](references/conditional-checks.md#matchers-on-serialized-input) and [classification-boundary](references/conditional-checks.md#classification-boundaries) checks to each new or changed decision. For review fixes meeting the risk trigger, apply the [review-fix delta checks](references/conditional-checks.md#review-fix-deltas) once per round. These are part of the baseline review within the selected scope.

For standard and deep, the coordinator must read [finder angles and reviewer roles](references/finder-and-verifier.md) in full before assigning or performing baseline passes. Use it for discovery, assignment, verification handoffs, and the deep gap sweep. If that read is missing or truncated, fail the run as `INCOMPLETE` until the read is completed; do not substitute a coverage-limit note, silently downgrade depth, or issue a merge verdict. This gate also applies to empty finding lists and compact output. Standard and deep must check enclosing functions, removed behavior, callers and changed callees, forwarding wrappers, exact repository rules, and whether a shared mechanism should own the fix. Preserve every candidate with a nameable failure scenario until verification; discovery does not retract candidates.

Keep a ledger of reference files actually read, using their paths. Claim an angle or checklist only after reading its owning reference; an unread applicable reference is a coverage limit. Start the report with `Scope: ...; references_read: <paths>; finder_passes: <completed>/<required>; partitions: <file/function partitions or ledger link>; limits: <unread checks and reduced coverage>`. Keep these fields in compact output too. Selecting a reference or receiving another reviewer's summary does not mean you read it; truncated output establishes only the portions actually shown.

Read [references/conditional-checks.md](references/conditional-checks.md) only for languages and change patterns present in the scope, including serialized-input matching, classification boundaries, invariants under event order, review-fix deltas, persisted shortcuts and retention, concurrent row writers, resumable scans, client failure paths, configuration/bootstrap changes, and tests that replace framework behavior. Load its [CI workflows checks](references/conditional-checks.md#ci-workflows) only when `.github/workflows/` or other CI configuration changes. Do not load or apply unrelated sections.

Load only the language references needed by changed behavior and its tests:

- Go: [references/review-go.md](references/review-go.md).
- TypeScript (`.ts`, `.tsx`, `.mts`, `.cts`), declarations, or related module/build configuration: [references/review-typescript.md](references/review-typescript.md).
- Python: [references/review-python.md](references/review-python.md).
- FastAPI endpoints, dependencies, response models, or streaming changes: also read [references/review-fastapi.md](references/review-fastapi.md) after establishing the installed FastAPI/Pydantic versions.
- PHP or PHP-backed templates: [references/review-php.md](references/review-php.md).
- Makefiles (`Makefile`, `makefile`, `GNUmakefile`, `*.mk`), shell scripts, hook commands, or CI steps: [references/review-shell.md](references/review-shell.md), including inline commands in configuration files. For CI configuration changes, also apply the conditional CI checks above.

Select language references by executed behavior, including inline programs in shell, CI, containers, and templates, rather than file extensions alone. In a mixed-language change, apply each reference to the relevant code and trace cross-language contracts once. These references refine the same evidence and severity rules; they are not separate verdicts or a request to apply one language's conventions to another. Language presence alone does not authorize a framework audit, dependency installation, formatter fix, or migration.

Use `fastapi-development` for requested FastAPI implementation, `claude-api` for requested Claude API integration, and `uv-project-workflow` for requested uv environment/dependency work. A diff using those technologies remains a read-only review here; do not invoke an implementation workflow to inspect it.

Load detailed references only when the changed paths make them relevant and local repository guidance does not already answer the question:

- [testing-patterns.md](references/testing-patterns.md) for JavaScript or TypeScript tests when its Jest, React Testing Library, Supertest, or Playwright examples match the repository's actual tools; otherwise use the local runner and the TypeScript review reference;
- [security-checklist.md](references/security-checklist.md) for web trust boundaries, authentication, authorization, input handling, dependency security, or LLM features;
- [performance-checklist.md](references/performance-checklist.md) for web performance, database, API, rendering, or resource-bound concerns;
- [accessibility-checklist.md](references/accessibility-checklist.md) for user-interface semantics and interaction changes;
- [observability-checklist.md](references/observability-checklist.md) for production logs, metrics, traces, alerts, and telemetry verification;
- [definition-of-done.md](references/definition-of-done.md) only when the repository defines a completion gate or the user asks for merge readiness.

Do not read all detailed references by default. Repository rules override these vendored snapshots, and any commands or measurements they suggest remain subject to the high-cost approval gate.

## Analyze applicable dimensions

Evaluate only dimensions touched by the change. Mark the rest `not-applicable`.

- correctness, requirements, and data flow;
- error handling, recovery, and partial failure;
- authentication, authorization, validation, secrets, and privacy;
- concurrency and lifecycle management;
- readability, control-flow simplicity, and dead code introduced by the change;
- public contracts, migrations, architecture, and repository rules;
- deletion, movement, and rename completeness;
- dependencies, lockfiles, and supply-chain boundaries;
- performance and resource bounds;
- edge cases and corrupt or empty external data;
- test coverage and test validity;
- logs, metrics, traces, units, polarity, and sensitive content.

For structural concerns, name the smallest useful move: remove an unnecessary abstraction, make a type boundary explicit, consolidate duplicate branches, separate orchestration from business logic, reuse the canonical helper, or move feature logic to its owning module. A refactor should remove concepts or branches, not merely relocate them.

## Generate candidates, then verify

The finder records stable CR IDs, location, category, a concise summary, and `inputs/state -> wrong result or crash` for every candidate with a nameable failure scenario. Record uncertainties without filtering or retracting candidates. Grounding is a later pass; a bare preference without a scenario is not a candidate.

When an Agent/subagent tool is available, assign one fresh verifier who did not find the candidates. Give it the diff, relevant files, applicable instructions, intended behavior, and candidate list, without the finder's reasoning or proposed verdicts. This verifier is part of the baseline, not an optional high-cost extension. Without that tool, verify inline after discovery and disclose the lack of an independent reviewer. Quick keeps the verifier within the same hunk-only scope.

The verifier re-reads the current lines and diff, traces the path, checks callers, guards, configuration, and tests, and considers the strongest intentional-design counterargument. Give each candidate one outcome:

- `CONFIRMED`: name the trigger and wrong result and quote the supporting line. Execution is useful but not required when the source trace establishes both.
- `PLAUSIBLE`: name the real mechanism and conditional trigger (timing, environment, configuration, or state), quote the relevant line, and state what would confirm it. Realistic races, nil on error/cold-cache/optional-field paths, partial failure plus retry, boundary off-by-one errors, and regex/allowlist anchor loss remain findings when not disproved.
- `REFUTED`: cite and quote contradicting code, an invariant or type making the scenario impossible, a guard in this diff, or a source trace proving no observable effect. A stronger-sounding counterargument, low frequency, a happy-path test, or lack of reproduction is not refutation.

Keep `CONFIRMED` and `PLAUSIBLE` in Findings with the verdict shown. Questions are only for hypotheses requiring evidence outside the repository, such as production data, database or prompt contents, or undocumented provider behavior. A source-grounded plausible mechanism stays in Findings even if a production sample would help confirm occurrence. Missing local inspection or unrun checks are verification limits, not a reason to park a candidate in Questions. Severity follows the demonstrated impact; uncertainty alone does not raise priority.

Exclude formatter-owned style, generated-file noise, and unrelated debt. An unchanged line inside a touched function is in scope when this change re-exposes its defect or the stated fix should have addressed it; explain that causal connection. Conventions require the exact quoted rule, its file path, and the violating line. Quantify impact only when evidence supports the estimate. References retain their technical checks; candidate disposition follows this three-outcome contract.

In deep mode, run the bounded gap sweep after verification and verify its additions the same way. A non-refuted verification vote retains the finding; unresolved disagreement with a refutation is shown as `PLAUSIBLE` with both pieces of evidence, not silently suppressed.

## Verify the verification story

Separate repository evidence from commands actually executed.

- Record relevant tests, builds, linters, type checks, manual checks, screenshots, or before/after evidence reported by the author or CI.
- Never say a command passed unless its result was observed.
- When behavior-defining data lives outside the repository (prompts, knowledge-base/rule rows, feature flags, remote config), record the source and capture time of any snapshot used as evidence and compare it with edits mentioned in the issue/PR discussion. A snapshot older than a known edit is a verification limit, not evidence of current content. Name the fresh read needed to confirm it; unknown capture time or edit chronology also limits verification.
- Treat passing tests as evidence, not proof that changed behavior is covered.
- Before requesting another test, name the concrete regression it should catch and check whether an existing case already covers it. Prefer the smallest useful extension over a parallel suite. Review added tests for brittle copy assertions and unrelated framework or global behavior using [the conditional test checks](references/conditional-checks.md#tests-and-verification); test counts and new public methods alone do not establish a coverage gap.
- For mocks or stubs on the changed path, identify the real selection, parsing, precedence, or persistence behavior they replace. Cite separate source or execution evidence for that behavior, or mark it unverified; mutation controls on orchestration do not validate a stubbed framework contract.
- Treat a coverage percentage as measured only when a coverage tool produced it for the relevant code.
- For a bug fix with a new regression test, identify the pre-fix behavior the test should reject. When the claim is important and a narrow negative control is proportionate, run the test against the pre-fix behavior in an isolated scratch copy, verify that the intended assertion fails, then verify the fixed behavior passes. Preserve the working checkout and other sessions' files. If the control was not run, state that the test was not observed failing for the defect; do not call it a proven regression test.

Run cheap, targeted, read-only checks or isolated scratch controls when they are normal for the repository and materially verify a candidate. Do not silently expand into the high-cost checks below.

Before the final verdict, revisit exclusions and assumptions that could hide a reachable failure in the changed path. A development-only label does not exclude supported configuration variants. Do not issue `APPROVE` while a material assumption remains unverified; record the missing evidence and a concrete check in the finding or verification limits, using Questions only for external-evidence hypotheses, and let that limit constrain the verdict.

## Learn from external review evidence

When third-party findings are supplied, read [external review learning](references/external-review-learning.md) to verify their claims and distinguish reusable improvements from local policy. This remains a read-only assessment unless skill or memory maintenance is already authorized.

## Offer high-cost checks only after the baseline report

Do not run token-, context-, time-, network-, or compute-intensive extensions outside the authorized review scope without approval after the baseline report. Existing authorization, repository-required checks, and bounded verification needed to resolve a material finding do not require another permission question. Judge actual scope, cost, and side effects rather than treating a command name as inherently expensive. Optional extensions can include:

- exhaustive repository-wide call-graph or dead-code analysis beyond affected contracts;
- full test suites, full builds, broad mutation-testing campaigns, or coverage generation;
- profiling, benchmarks, load tests, or bundle analysis;
- broad security, dependency-advisory, supply-chain, accessibility, or observability audits;
- external changelog, migration-guide, maintenance, license, or vulnerability research;
- additional sub-agent, model, or council review beyond the baseline finder/verifier and requested deep sweep.

After completing every other report section, list only plausible extensions and give each:

- the proposed check and bounded scope;
- context/token cost and runtime or side-effect cost as `low`, `medium`, or `high`;
- the evidence it could add;
- the potential impact on findings, confidence, or merge verdict;
- a `worth running` or `not worth running` recommendation with one-sentence rationale.

Ask one bundled approval question at the very end only for checks marked `worth running` that lack existing authorization. Do not ask about low-value checks merely because they are available. If none is worth running, say so without asking a question.

## Priority, disposition, and verdict

Use stable IDs independent of severity: `CR-001`, `CR-002`, and so on.

- `P0`: immediate security, safety, or irreversible-loss blocker.
- `P1`: material correctness or security issue that should block merge.
- `P2`: meaningful reliability, test, or maintainability risk.
- `P3`: optional evidence-backed improvement.

Use one disposition: `open`, `question`, or `retracted`. Both `CONFIRMED` and `PLAUSIBLE` findings are `open`. Only externally dependent hypotheses are `question`; only evidence-backed `REFUTED` candidates are `retracted`. Keep refutations in the verification record, not the public findings list. Stable IDs survive sorting, deduplication, truncation, and later fixes.

Return one verdict:

- `APPROVE`: no open blocker and no material unverified risk;
- `COMMENT`: useful non-blocking findings or bounded verification limits remain;
- `REQUEST_CHANGES`: at least one open P0/P1 finding makes the change unsafe to merge.

## Report

For the full report, return in this order:

1. scope and intent: one scope line with base, included change sources, path filters, exclusions, assumptions, paths of every reference actually read, and required/completed finder passes with partitions and reduced-coverage areas;
2. review depth: files and tests inspected, traces performed, and baseline limits;
3. applicable-dimension summary with `pass`, `concern`, or `not-applicable`;
4. confirmed and plausible findings ordered by priority, each with its verification verdict;
5. actionable changed-path test coverage;
6. verification evidence and commands not run;
7. questions and verification limits;
8. one or two grounded strengths when present;
9. verdict;
10. when external review evidence was considered, the skill-improvement assessment, distinguishing reusable changes from scoped project or organization memory;
11. optional high-cost checks and, only when warranted, the final approval question.

Use this finding shape:

```text
ID: CR-001
Priority: P1
Disposition: open
Location: path/to/file:line
Summary: <one sentence>
Failure scenario: <inputs/state -> wrong result or crash>
Verdict: CONFIRMED | PLAUSIBLE
Category: correctness | security | reliability | performance | coverage | cleanup | conventions
Evidence: <quoted relevant line and traced call/data path; rule path and quote for conventions>
Impact: <concrete failure and affected users or systems>
Counterargument: <strongest plausible intentional rationale>
Confirmation: <for PLAUSIBLE: the observation or check that would confirm it>
Remediation: <smallest safe approach>
```

Use this test-coverage shape:

```text
Significant changed paths:
- <behavior or path> — covered | partial | uncovered | unknown — <test file:test name or evidence>

Missing tests, ordered by risk:
1. <P1/P2/P3> <scenario or topic> — path: <changed behavior>; level: <unit/integration/e2e/etc.>; catches: <specific regression>
```

Every `partial` or `uncovered` status must map to at least one missing-test item. Do not report only that coverage is incomplete. If evidence is unavailable, use `unknown`, explain what is missing, and give the exact verification step. Write `None` only when all significant changed paths have grounded coverage evidence.

Before applying `--max-findings`, deduplicate by failure mechanism, then sort by P0 through P3. At equal priority, correctness/security/reliability outrank performance/coverage, which outrank cleanup/conventions; preserve CR-ID order within a tier. Report the number cut, even zero. A cap never changes the verdict derived from all retained findings and material verification limits. Use [the report contract](references/report-contract.md) and `scripts/prepare_review_report.py` to validate structured findings, including the coordinator's `references_read` ledger, and apply the cap when Python is available; otherwise apply the same rules and mandatory-read gate inline and disclose that the mechanical check was not run.

For `--format compact`, emit only: one scope line (including depth, reviewer independence, read-reference paths, required/completed passes and partitions, verification limits and cut count), Findings using the CR block, coverage mapping and gaps, and the merge verdict. Keep the explicit `Failure scenario` and `Verdict` labels in each finding; shorten their values, not the evidence fields. Put any essential external-evidence question or external-review learning assessment in the scope/limits line. Omit the dimension table, strengths, and high-cost offers or approval questions. Coverage still covers every significant path, but must not re-render cut findings to bypass the display cap. Compact changes presentation, not verification.

If the caller asks for host rendering and a `ReportFindings` tool is exposed, use its actual schema to report file, line, summary, `short_summary` (at most 60 characters), failure_scenario, category, and verification verdict. Keep CR-ID mapping and the text coverage/verdict summary. If fixes are later authorized in the same session, re-verify the affected findings and re-report with the supported outcome (fixed, unresolved, or refuted); do not infer a fix from an author's claim. If the tool is absent or lacks a field/outcome, report the limit and use the text report rather than inventing tool capabilities.

When no findings remain after verification, say so clearly and retain any coverage or verification limits; distinguish no findings from all findings cut by a display cap. Never edit reviewed files, stage, commit, push, or comment on the pull request as part of this review. Only the explicitly requested report artifact and host rendering are allowed as described above; file handoff returns the short response instead of rendering findings again.
