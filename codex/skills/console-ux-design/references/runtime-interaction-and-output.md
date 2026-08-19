# Runtime interaction and output

## Contents

- [Model the interaction as states](#model-the-interaction-as-states)
- [Design prompts](#design-prompts)
- [Handle secrets, EOF, and timeouts](#handle-secrets-eof-and-timeouts)
- [Confirm destructive work](#confirm-destructive-work)
- [Communicate status and progress](#communicate-status-and-progress)
- [Write errors for recovery](#write-errors-for-recovery)
- [Adapt to terminals and redirection](#adapt-to-terminals-and-redirection)
- [Lay out text and data](#lay-out-text-and-data)
- [Use color and symbols redundantly](#use-color-and-symbols-redundantly)
- [Control verbosity](#control-verbosity)
- [Support Unicode, localization, and accessibility](#support-unicode-localization-and-accessibility)
- [Handle cancellation and cleanup](#handle-cancellation-and-cleanup)
- [Write concise console copy](#write-concise-console-copy)
- [Specify the runtime experience](#specify-the-runtime-experience)

## Model the interaction as states

Describe the runtime as a state machine rather than a happy-path transcript. Name states such as:

- invocation validation;
- ready to start;
- awaiting input;
- working with known or unknown progress;
- retrying or waiting on a dependency;
- succeeded;
- failed before changes;
- failed after partial changes;
- cancelled and cleaning up.

For each state define entry conditions, visible feedback, allowed user actions, time-dependent behavior, transitions, side effects, and the stream and exit result. Include invalid input, EOF, cancellation, dependency failure, and partial work.

Keep the state model small. Combine states that look and behave the same to the user; separate states when recovery or side effects differ. Ensure every waiting state explains what the program is waiting for when that information is useful.

## Design prompts

Prompt only for information the program cannot safely infer and the user has not supplied explicitly. Group related questions in task order and expose advanced choices only when they become relevant.

Each prompt should provide:

- a concise question in domain language;
- accepted input forms or visible choices;
- a safe default when one exists;
- validation and a correction path;
- a non-interactive equivalent;
- explicit treatment of empty input, EOF, and cancellation.

Show defaults in the prompt and define whether an empty response accepts them. Do not present a default that could surprise the user or broaden the target. Preserve previously valid answers when retrying a later field.

Validate as soon as the program has enough information to give a useful correction, but avoid remote or destructive work during input collection. On invalid input, explain the constraint and ask again only when input is interactive. In non-interactive operation, fail once with an actionable diagnostic.

Avoid making users recall opaque identifiers when the program can safely list or complete candidates. Keep choices distinct and consistently named. For large or dynamic sets, support explicit identifiers and completion rather than dumping an unbounded menu.

## Handle secrets, EOF, and timeouts

Read secrets through a non-echoing mechanism when interactive input is appropriate. Prefer references to secret stores or environment-managed credentials for automation. Never place secrets in examples, progress, error context, shell history guidance, debug logs, or machine output.

Treat EOF as a distinct input condition, not as consent or an empty answer. If required input is unavailable, stop before side effects and explain how to supply it explicitly.

When external waits or prompts can time out, state whether the timeout is configurable, what operation stopped, whether work occurred, and how to retry safely. Do not add arbitrary timeouts to local reading tasks merely to create motion.

## Confirm destructive work

Prevent destructive mistakes before polishing the confirmation wording.

- Validate and resolve the exact target before asking.
- Summarize material scope and irreversible consequences.
- Make the safe answer the default.
- Require an unambiguous response; EOF, timeout, or invalid input must not proceed.
- Reconfirm if the resolved target changes after the prompt.
- If the resolved target changes in non-interactive or force mode, abort before side effects and require a fresh invocation; force never authorizes target drift.
- Avoid repeated low-value confirmations that train users to approve blindly.

Provide a deliberate non-interactive override such as a framework-conventional force option only when automation legitimately needs it. The override authorizes confirmation bypass, not missing targets, broader scope, invalid input, or suppressed errors.

Provide a dry-run or plan mode when the command can preview meaningful effects. A dry run must avoid writes and external side effects, identify assumptions, use the same target resolution as real execution, and make its output distinguishable from completed work.

Prefer reversible operations, backups, transactions, or staged application when the domain supports them. Explain recovery before execution when reversal is not possible.

## Communicate status and progress

Feedback should answer the question appropriate to the delay:

- Did the command start?
- What phase is active?
- Is measurable progress being made?
- Is the program waiting or retrying?
- What completed, and what result should the user use next?

Use determinate progress only when the denominator and advancement are meaningful. Otherwise report stable phases or occasional status updates. Never fabricate precision.

Keep progress on the diagnostic channel so redirected results remain clean. When the diagnostic stream is not a terminal, emit durable line-oriented updates only when callers need them; avoid carriage-return animation, cursor movement, spinners, or noisy per-item chatter.

For fast operations, a final result is usually enough. For long work, report significant phase changes and provide item counts or identifiers only when they support trust or recovery. Rate-limit repeated updates rather than flooding logs.

On completion, state the outcome, relevant counts or artifacts, skipped or partial items, and the next action when one is required. Do not celebrate routine success at the expense of scannability.

## Write errors for recovery

An actionable error separates:

1. what failed in user or domain terms;
2. the relevant target or operation;
3. why, when known and safe to disclose;
4. what the user can do next;
5. where deeper diagnostics are available when needed.

Do not blame the user, expose a raw stack trace by default, or replace a specific failure with a generic “something went wrong.” Preserve the underlying cause for verbose or debug diagnostics without leaking secrets.

Prevent errors through early validation, explicit conflicts, safe defaults, and preflight checks. When an error occurs after partial work, enumerate completed, skipped, rolled-back, and unresolved effects. Give a retry command only if retrying is safe; otherwise explain cleanup or reconciliation.

Keep warning, error, cancellation, and domain-negative results distinct. Pair each with the exit category from the command contract.

## Adapt to terminals and redirection

Evaluate standard input, standard output, and standard error independently. A process can read from a pipe while writing results to a terminal, or write results to a file while showing diagnostics in a terminal.

Terminal-attached output may use adaptive width, color, concise in-place progress, and prompts when input is also interactive. Redirected output must remain durable, line-oriented, free of cursor control, and suitable for logs or downstream parsing.

Do not silently change the result schema based on terminal detection. Terminal detection may change human presentation, never the meaning of success, failure, or selected machine format.

Provide explicit overrides for behavior callers must guarantee, such as non-interactive, color-disabled, or structured output. Treat terminal detection as a useful default rather than the only control surface.

## Lay out text and data

Design for unknown terminal width:

- wrap prose at word boundaries without losing indentation or semantic prefixes;
- keep commands, paths, identifiers, URLs, and machine tokens intact where splitting would make copying unsafe;
- use hanging indentation for multi-line options and diagnostics;
- keep related label/value pairs visually grouped;
- place the most decision-relevant columns first;
- omit or abbreviate secondary human-only columns when width is constrained, while offering a detailed or structured form;
- avoid truncating unique identifiers without a way to retrieve or copy the full value.

Use tables only when aligned comparison improves scanning. Provide a plain line-oriented fallback for narrow terminals, redirected output, complex scripts, or values containing newlines. Do not encode meaning solely through column position.

Keep headings and blank lines proportional to the amount of output. Dense expert output may be appropriate when names and grouping remain predictable; do not enforce a universal line-length or item-count threshold.

## Use color and symbols redundantly

Treat ANSI styling as enhancement. Every status must remain understandable when color is disabled, unsupported, stripped, or indistinguishable.

- pair color with words, stable prefixes, symbols, or structure;
- keep semantic mappings consistent across commands;
- respect the project's established no-color convention and explicit override;
- disable control sequences in machine output and normally in redirected human output;
- avoid using decoration as evidence that work succeeded.

Choose symbols with a plain-text fallback. Account for font coverage, ambiguous character width, combining characters, and terminals that cannot render a chosen glyph. Do not assume emoji are single-column or universally legible.

## Control verbosity

Define a small, consistent verbosity model:

- default output communicates the requested result and material warnings;
- quiet mode suppresses routine human status but not failures and must not redefine the result;
- verbose levels add decision-relevant operational context;
- debug mode may expose implementation detail but must still redact secrets.

State whether repeated verbosity flags accumulate or a named level is used. Apply the same model across commands. Machine-readable output should not gain prose when verbosity increases; route diagnostics separately or add schema-governed diagnostic fields only when the format defines them.

## Support Unicode, localization, and accessibility

Use locale-aware formatting for human dates, times, numbers, and messages when localization is supported. Keep machine formats locale-neutral and document their encoding and timestamp conventions.

Do not assemble sentences from translated fragments. Allow messages and headings to expand, and test scripts with different character widths and combining behavior. Keep option and command names stable unless the product explicitly supports localized command grammars with a compatibility strategy.

Make output usable without color, rapid animation, or precise cursor tracking. Prefer durable text that can be selected, copied, searched, logged, and consumed by assistive tooling. Avoid continuous redraws that erase context. Provide text equivalents for symbols and progress.

## Handle cancellation and cleanup

Define behavior for interrupt and termination signals supported by the platform and framework:

- whether the current unit completes or stops immediately;
- which temporary resources, locks, child processes, and terminal modes are cleaned up;
- whether changes are rolled back, committed, or left partial;
- what diagnostic and exit result the caller receives;
- how a user can inspect or resume safely.

An interrupt must not leave the terminal in a broken presentation state. Keep cleanup bounded and make repeated interruption behavior deliberate. Do not claim atomicity when external effects cannot be rolled back.

## Write concise console copy

Use the user's vocabulary and consistent terms. Lead with the action or outcome. Prefer concrete verbs over vague labels, and keep instructions close to the decision they support.

For prompts, say what decision is required. For progress, say what phase is active. For errors, say what failed and how to recover. For success, say what changed or where the result is available.

Avoid jokes, blame, promotional filler, unexplained abbreviations, and anthropomorphic personality in high-stakes or failure messages. Adjust tone to severity without changing terminology. Write examples with realistic but non-sensitive values.

## Specify the runtime experience

Produce, as applicable:

1. a state and transition table;
2. prompt text, accepted answers, defaults, validation, EOF, and non-interactive equivalents;
3. destructive confirmation, force, and dry-run rules;
4. progress and completion behavior by stream and terminal attachment;
5. error, partial-work, retry, and recovery behavior;
6. layout rules for normal, narrow, redirected, and structured output;
7. color, symbol, quiet, verbose, Unicode, locale, and accessibility behavior;
8. cancellation, cleanup, and exit mapping;
9. representative transcripts with secrets redacted.

Use [validation.md](validation.md) to cover each state and operating context.
