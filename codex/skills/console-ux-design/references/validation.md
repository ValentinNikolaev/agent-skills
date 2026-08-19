# Console UX validation

## Contents

- [Derive checks from tasks and contracts](#derive-checks-from-tasks-and-contracts)
- [Exercise novice, expert, and automation flows](#exercise-novice-expert-and-automation-flows)
- [Verify discovery](#verify-discovery)
- [Verify prompts and input](#verify-prompts-and-input)
- [Verify streams, terminals, and formats](#verify-streams-terminals-and-formats)
- [Verify failures, destructive work, and cancellation](#verify-failures-destructive-work-and-cancellation)
- [Choose durable test techniques](#choose-durable-test-techniques)
- [Use framework-native tests as examples](#use-framework-native-tests-as-examples)
- [Prepare implementation handoff](#prepare-implementation-handoff)
- [Complete the release checklist](#complete-the-release-checklist)

## Derive checks from tasks and contracts

Validate the command as a public interface, not only as a function that returns the right data. Start from the approved task flows, command contract, and runtime state model.

For each scenario record:

- actor and operating context;
- invocation and supplied input;
- terminal attachment for input, output, and error;
- expected side effects and result;
- expected output and error-stream properties;
- expected exit category and numeric code;
- recovery or next action;
- contract element protected by the check.

Cover the happy path first, then branch at every decision, validation boundary, external dependency, and partial-work point. Prefer scenarios that reveal a distinct risk over a large matrix of cosmetic permutations.

## Exercise novice, expert, and automation flows

### Novice flow

Verify that a user who knows the task but not the command syntax can:

1. find the command from the root list or a predictable namespace;
2. understand its purpose and side effects from help;
3. construct a minimal valid invocation or follow safe prompts;
4. recognize progress, success, failure, and cancellation;
5. recover from a realistic invalid input without external explanation.

Observe misleading names, unexplained prerequisites, hidden defaults, ambiguous choices, and recovery steps that require implementation knowledge.

### Expert flow

Verify that a frequent user can:

- supply all required values explicitly;
- use completion and concise help without traversing prompts;
- select quiet, verbose, dry-run, force, and output modes consistently where supported;
- repeat the command safely and predict its idempotency or duplicate-effect behavior;
- copy commands and identifiers without presentation artifacts.

### Automation flow

Run without an interactive terminal. Verify:

- no prompt, spinner, cursor control, or indefinite input wait appears;
- required missing input fails before side effects;
- results and diagnostics remain on their assigned streams;
- the exit code matches the documented category;
- structured output remains parseable on success and defined failure cases;
- locale, width, color, verbosity, and environment do not silently alter the schema;
- secrets do not appear in output, diagnostics, traces, or recorded fixtures.

## Verify discovery

Test the root command list, namespace lists, command help, invalid-invocation help, examples, version output, and completion.

Check that:

- canonical commands appear in the expected group with outcome-oriented summaries;
- help usage matches the parser;
- arguments, options, defaults, conflicts, repeatability, modes, and side effects are accurate;
- examples parse after replacing explicit placeholders;
- deprecated aliases point to the replacement without dominating discovery;
- completion offers canonical names and values, remains side-effect free, and has a safe fallback when dynamic data is unavailable;
- an unknown command or option suggests only plausible alternatives and still returns the documented failure code.

Treat drift between parser, help, examples, and completion as a contract defect.

## Verify prompts and input

For every prompt, exercise:

- an explicit valid answer;
- acceptance of a documented default;
- empty input when no default exists;
- invalid input followed by correction;
- repeated invalid input according to the intended retry policy;
- EOF before and during the prompt sequence;
- user cancellation;
- the equivalent explicit non-interactive invocation;
- redirected standard input when supported;
- timeout behavior when a real external wait or input deadline exists.

Verify that an empty response, EOF, timeout, and affirmative response are never conflated. Confirm that earlier valid answers survive later correction when promised. Ensure validation occurs before irreversible side effects.

For secrets, verify input is not echoed and the value is redacted from every output mode, verbosity level, error path, trace, and test artifact.

## Verify streams, terminals, and formats

Test input, output, and error terminal attachment independently rather than as one Boolean mode. Include representative combinations:

- all streams attached to a terminal;
- result output redirected with diagnostics attached;
- result output attached with input piped;
- both output streams captured separately;
- non-interactive input with human output;
- machine format with diagnostic output captured.

Check standard output contains only the requested result contract and standard error contains diagnostics, warnings, and progress according to the specification. Compare semantics across attached and redirected operation; presentation may adapt, meaning must not.

For human output, exercise normal and narrow widths, long paths and identifiers, empty data, many rows, embedded whitespace, and values that cannot be safely truncated. Verify wrapping, hanging indentation, table fallback, and copyability.

For color and symbols, exercise automatic behavior plus explicit color-disabled or plain output. Strip ANSI sequences and confirm that status, severity, and grouping remain understandable. Test a plain ASCII fallback when the supported environment may lack glyph coverage.

For Unicode and localization, include non-ASCII paths and data, combining characters, wide characters, translated messages, differing human number/date formats, and a locale-neutral machine format. Verify encoding failures are reported without corrupting unrelated output.

## Verify failures, destructive work, and cancellation

Exercise failures before work, during one unit of work, after partial work, during cleanup, and while reporting the result.

For each failure verify:

- the diagnostic names the operation and relevant target without leaking secrets;
- the recovery action is valid for that state;
- completed, skipped, rolled-back, and unresolved effects are distinguished;
- retry advice is given only when retry is safe;
- the exit category and code match the contract;
- machine output remains valid or is intentionally absent according to its contract.

For destructive commands verify target resolution, scope summary, safe default, affirmative and negative answers, invalid answer, EOF, non-interactive refusal, authorized force behavior, and target change between planning and execution.

Verify dry-run mode uses real validation and target resolution while producing no writes, remote changes, notifications, locks, or persistent temporary data. Compare its planned actions with a controlled real execution to detect planning drift.

For cancellation and supported signals, interrupt during validation, active work, and cleanup. Verify bounded cleanup, child-process handling, terminal restoration, locks and temporary files, partial-work reporting, exit behavior, and safe resume or reconciliation instructions.

## Choose durable test techniques

Use the narrowest test that protects each contract:

- parser tests for signatures, precedence, defaults, conflicts, and aliases;
- command-level integration tests for streams, exit codes, prompts, progress, cancellation, and side effects;
- schema tests for machine-readable output;
- transcript tests for important end-to-end journeys;
- golden or snapshot tests for stable help structure, tables, and protocol-like text;
- property-based tests for quoting, arbitrary input values, width boundaries, Unicode, serialization, and parser invariants;
- manual or pseudo-terminal tests for terminal detection, cursor behavior, signal handling, and secret echo where the test harness cannot model them faithfully.

Snapshots should protect intentional contracts: usage grammar, option presence, stream boundaries, schema shape, safety warnings, and stable examples. Avoid snapshots that fail only because harmless prose, spacing, ordering without semantic meaning, or framework-generated wording changed. Prefer semantic assertions for variable content and focused snapshots for structures users or scripts rely on.

Normalize only nondeterministic values such as temporary paths, timestamps, generated identifiers, or timing. Do not normalize away the target, stream, exit code, ordering guarantee, or error category being tested.

## Use framework-native tests as examples

Use the project's installed framework and version rather than assuming an API. Framework-native console test helpers can often:

- invoke a command with arguments and options;
- provide expected prompt answers;
- assert output or error text;
- assert table or choice behavior;
- inspect an exit code;
- fake or capture events and side effects.

Laravel Artisan command tests and Symfony Console command/tester facilities are useful examples of this pattern, not universal interfaces. Inspect current project documentation and existing tests before selecting helpers. Supplement framework helpers when they do not accurately model separate streams, redirected output, pseudo-terminals, signals, or shell completion.

Do not make a test pass by changing the user contract to fit a convenient helper.

## Prepare implementation handoff

Give implementers behavior, states, and contracts rather than visual redlines. Include:

1. approved command tree and signatures;
2. input precedence, defaults, validation, conflicts, and secret rules;
3. list, help, examples, and completion requirements;
4. state transitions, prompts, progress, error, retry, and cancellation behavior;
5. stream ownership, output formats, schema/versioning, terminal adaptation, and verbosity;
6. exit taxonomy and numeric mapping;
7. destructive confirmation, force, dry-run, rollback, and partial-work rules;
8. compatibility, alias, deprecation, and migration decisions;
9. acceptance scenarios and which layer should test each one;
10. unresolved product or platform decisions.

Provide representative before-and-after transcripts with separate standard output, standard error, and exit result when that distinction matters. Label wording that is illustrative rather than contractually frozen.

## Complete the release checklist

Before handoff or release, confirm:

- [ ] Command names and grouping reflect user tasks and established conventions.
- [ ] Parser, help, examples, and completion agree.
- [ ] Arguments, options, defaults, precedence, and conflicts are documented and tested.
- [ ] Interactive and non-interactive operation reach the same supported outcomes.
- [ ] Missing input, EOF, invalid input, timeout, and cancellation fail safely.
- [ ] Standard output, standard error, and exit codes follow the approved contract.
- [ ] Human output works at representative widths and under redirection.
- [ ] Machine output is syntactically pure and its schema compatibility is protected.
- [ ] Color-disabled, plain, Unicode, and relevant locale cases preserve meaning.
- [ ] Quiet, verbose, and debug behavior is consistent and secrets stay redacted.
- [ ] Destructive confirmation, force, dry-run, partial work, retry, and cleanup are verified.
- [ ] Aliases and deprecations have migration coverage.
- [ ] Snapshots protect contracts rather than incidental wording.
- [ ] Framework-specific helpers are supplemented where they cannot model the real process boundary.
- [ ] The final handoff distinguishes verified behavior, assumptions, and remaining decisions.

