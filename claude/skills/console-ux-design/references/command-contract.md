# Console command contract

## Contents

- [Start from tasks and conventions](#start-from-tasks-and-conventions)
- [Build the command taxonomy](#build-the-command-taxonomy)
- [Name commands consistently](#name-commands-consistently)
- [Design arguments, options, and defaults](#design-arguments-options-and-defaults)
- [Make commands discoverable](#make-commands-discoverable)
- [Define interactive and non-interactive behavior](#define-interactive-and-non-interactive-behavior)
- [Protect automation and CI](#protect-automation-and-ci)
- [Separate streams and output formats](#separate-streams-and-output-formats)
- [Define a stable exit taxonomy](#define-a-stable-exit-taxonomy)
- [Evolve the contract deliberately](#evolve-the-contract-deliberately)
- [Specify the contract](#specify-the-contract)

## Start from tasks and conventions

Inventory the current executable, command tree, aliases, global options, configuration, environment variables, help, completion, exit codes, output formats, and supported scripts before proposing a change.

Model commands around user tasks rather than internal classes, services, or repository folders. Record for each task:

- actor: novice, frequent operator, administrator, or automation;
- goal and expected result;
- required knowledge and inputs;
- side effects, reversibility, and failure cost;
- frequency and whether composition with other tools matters;
- established framework or ecosystem convention.

Follow familiar conventions unless the task provides evidence that they fail. A novel grammar makes every user learn local rules and makes completion, documentation, and automation harder. When departing from a convention, name the convention, the observed problem, the replacement, and the migration cost.

Eliminate accidental complexity. Let the program infer safe, unambiguous facts; use defaults for common low-risk choices; expose control where the user must make a meaningful decision. Never hide consequential behavior behind an unexplained default.

## Build the command taxonomy

Construct a shallow, task-centered tree:

- group related commands under stable domain namespaces;
- keep common tasks easy to find from the root list;
- separate different outcomes rather than accumulating unrelated modes in one command;
- keep one concept at one level of the tree;
- avoid a namespace containing both an action and a different command with the same word;
- reserve global options for behavior that is truly consistent across commands.

Prefer meaningful chunks over arbitrary item-count rules. Experts can scan larger sets when names are predictable; novices need clear groups and summaries. Add depth only when it reduces ambiguity, not to mirror code ownership.

For each command, state its one-sentence task and its relationship to siblings. Merge commands whose only difference is presentational. Split commands when they have different permissions, side effects, success criteria, or automation contracts.

## Name commands consistently

Define a naming grammar before naming individual commands. Specify:

- verb–object or domain–action order;
- tense and grammatical form;
- separator and casing conventions;
- singular/plural treatment;
- vocabulary for create, inspect, change, remove, validate, and synchronize operations;
- reserved words and global option names.

Choose words users already encounter in the domain. Use the same term in command names, arguments, options, help headings, progress, errors, and documentation. Do not alternate synonyms for variety.

Names must distinguish outcomes. Avoid vague verbs such as `run`, `do`, `manage`, or `process` when a domain action is available. Keep abbreviations only when the audience reliably knows them. Prefer a readable canonical name over a short alias.

## Design arguments, options, and defaults

Use positional arguments for required identity or the primary object when order remains obvious. Use named options for optional behavior, modifiers, repeated values, credentials references, formats, and inputs whose order would be ambiguous.

For every input define:

- canonical name and any short form;
- type, accepted forms, and normalization;
- required, optional, repeatable, or mutually exclusive status;
- source precedence among explicit input, configuration, environment, inferred value, and default;
- validation timing and actionable failure message;
- whether the value is safe to echo, log, or include in diagnostics.

Make defaults visible in help when they materially affect results. A default must be safe in the user's context, deterministic enough for automation, and overridable. Do not default a destructive target, security-sensitive choice, or ambiguous environment.

Define conflicts and implications explicitly. Reject incompatible options before side effects begin. If one option implies another, either make that implication part of the documented contract or require both; do not leave it accidental.

Keep flags orthogonal. If a Boolean flag acquires several meanings, replace it with a clearly named mode or separate commands. Prefer repeatable options or input files to fragile delimiter grammars.

## Make commands discoverable

Treat list, help, examples, and completion as one navigation system.

The root list should:

- group commands by user task or domain;
- pair each command with a concise outcome-oriented summary;
- reveal how to request command-specific help;
- keep deprecated aliases out of the primary path while still explaining them when invoked.

Command help should show:

- purpose and important side effects;
- usage grammar;
- arguments and options with defaults, conflicts, and repeatability;
- interactive and non-interactive differences;
- output formats, streams, and meaningful exit behavior;
- a minimal successful example plus risk or automation examples when relevant;
- where to find deeper documentation without making it necessary for basic use.

Examples must be runnable after replacing clearly marked placeholders. Do not expose real secrets, machine-specific paths, or an unquoted syntax that fails in supported shells.

Completion should use the same canonical names and allowed values as parsing and help. Keep completion fast and side-effect free. Do not make network access, authentication, or expensive discovery an invisible requirement; provide a bounded or static fallback.

## Define interactive and non-interactive behavior

Declare whether each command supports:

- fully non-interactive execution from explicit arguments and options;
- optional prompting when required information is missing;
- an explicitly interactive workflow;
- standard-input data or response consumption.

Do not infer interactivity from standard output alone. Consider input, output, and error streams independently because any subset may be attached to a terminal or redirected.

When required information is missing in non-interactive mode, fail before side effects with a diagnostic that names the missing input and its explicit form. Do not wait indefinitely for input, select an unsafe answer, or silently change behavior.

If prompts are a convenience layer, ensure that explicit arguments and options can express the same supported operation. Document precedence when both prompt input and explicit values exist.

## Protect automation and CI

An automation-safe command has a documented, stable contract:

- no surprise prompts or terminal-only control sequences;
- deterministic parsing and conflict handling;
- stable success/failure exit categories;
- parseable output when structured consumption is supported;
- diagnostics kept separate from result data;
- bounded retry and timeout behavior where external systems are involved;
- no dependence on current directory, locale, color, or terminal width unless explicitly documented;
- explicit confirmation bypass for pre-authorized destructive automation, with all required targets supplied.

Do not treat detection of a CI environment variable as the only non-interactive control. Provide an explicit mode when callers need a guarantee, and make unsafe ambiguity fail closed.

## Separate streams and output formats

Assign stream ownership before writing messages:

- standard output carries the requested result or selected machine-readable document;
- standard error carries diagnostics, warnings, progress, and failure explanations;
- help and version output follow the host framework's documented convention consistently.

Do not duplicate ordinary success output across streams. Redirection must not change the semantic result.

When supporting human and machine formats, define them as separate contracts. Human output may adapt to terminal width and verbosity. Machine output must remain syntactically pure, schema-governed, and free from decoration, progress, headings, or commentary.

Specify machine-format behavior for empty results, warnings, partial data, timestamps, identifiers, numeric precision, ordering, and null or absent fields. Prefer adding fields compatibly; version the schema or format when consumers cannot safely ignore a change.

## Define a stable exit taxonomy

Define project-level exit categories before assigning numeric values. At minimum distinguish successful completion from failure. Add categories only when callers can act differently, such as:

- invalid invocation or input;
- rejected precondition or user cancellation;
- unavailable dependency or transient external failure;
- permission or authentication failure;
- completed work with a domain-negative result, when that result is not an execution error;
- partial completion when the application truly permits it.

Map categories to stable numeric codes using project, framework, and platform conventions. Document whether cancellation, validation findings, empty results, or warnings count as success. Do not return success after failing the requested task merely because an error message was printed.

Keep human wording independent from the exit taxonomy so copy can improve without breaking automation.

## Evolve the contract deliberately

Treat command names, option names, defaults, exit meanings, stream placement, and machine schemas as public interfaces once scripts may depend on them.

For a compatible rename:

1. introduce the new canonical form;
2. keep the old form as an alias when feasible;
3. emit a concise deprecation diagnostic without corrupting machine output;
4. show the replacement in help and examples;
5. test both forms during the announced migration window;
6. remove the alias only under the project's versioning policy.

Do not reuse an old name for a new meaning. Document breaking changes and provide mechanical migration guidance. Keep aliases out of completion when the goal is to move users to the canonical form.

## Specify the contract

Produce a reviewable command contract containing:

1. task and audience;
2. command tree and naming rules;
3. signatures with input types, precedence, defaults, conflicts, and secret handling;
4. list, help, examples, and completion behavior;
5. interactive and non-interactive rules;
6. standard-output and standard-error ownership;
7. human and machine formats;
8. exit categories and numeric mapping;
9. aliases, deprecations, and compatibility promises;
10. representative invocations with expected streams and exit results.

Use [validation.md](validation.md) to turn the contract into acceptance criteria.

