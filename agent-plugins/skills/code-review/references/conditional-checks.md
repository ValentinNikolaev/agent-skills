# Conditional Review Checks

Read only the sections that match the changed languages or change patterns.

## Contents

- [Tests and verification](#tests-and-verification)
- [Matchers on serialized input](#matchers-on-serialized-input)
- [Classification boundaries](#classification-boundaries)
- [Invariants under event order](#invariants-under-event-order)
- [Review-fix deltas](#review-fix-deltas)
- [Persisted shortcuts guarded at write time](#persisted-shortcuts-guarded-at-write-time)
- [Configuration and bootstrap](#configuration-and-bootstrap)
- [CI workflows](#ci-workflows)
- [Build and runtime identity](#build-and-runtime-identity)
- [Recoverable failures and process lifetime](#recoverable-failures-and-process-lifetime)
- [Locking and callbacks](#locking-and-callbacks)
- [Concurrent writers of the same rows](#concurrent-writers-of-the-same-rows)
- [Resumable scans and pagination](#resumable-scans-and-pagination)
- [Optimization claims](#optimization-claims)
- [Readability and architecture](#readability-and-architecture)
- [Dependencies and lockfiles](#dependencies-and-lockfiles)
- [Web UI and accessibility](#web-ui-and-accessibility)
- [Queues and retrying workers](#queues-and-retrying-workers)
- [Multi-system writes](#multi-system-writes)
- [Dependency injection and registries](#dependency-injection-and-registries)
- [External services and fallbacks](#external-services-and-fallbacks)

## Tests and verification

- Prefer behavior assertions over implementation-detail assertions that break during safe refactors.
- Identify the change-owned regression each added or requested test distinguishes. Search nearby coverage first; prefer extending an existing case or parameterizing equivalent inputs over duplicate suites. Keep separate cases when they exercise different failure paths. Similar setup alone does not establish redundant coverage.
- Follow repository policy for human-facing messages and translations. Unless exact wording is an explicit contract, prefer dynamic values, links, conditional content, formats, and escaping over literal greetings, subjects, footers, or translated sentences. Preserve exact checks for contractual bytes, stable error codes, and security-sensitive transformations.
- Keep tests scoped to behavior owned or changed here. Do not request tests of unrelated application-wide defaults or established framework guarantees unless the changed integration can break them. Flag brittle or redundant assertions only with a concrete maintenance cost or coverage weakness, not a target test count.
- In locale, configuration, or platform matrices, distinguish exercising each variant from proving variant-specific behavior. Shared data assertions can pass while a fallback masks a missing variant; record that limit unless the missing distinction violates the accepted contract. Any proposed discriminating check must respect repository test policy rather than automatically adding exact human-facing strings.
- For a bug fix, identify the regression test that fails without the fix and passes with it; if absent, name the exact missing scenario.
- Check happy path, the highest-risk edge case, and meaningful error or partial-failure behavior introduced by the change.
- Mock system boundaries such as databases, clocks, filesystems, and remote services; do not mock the business logic under test without a repository-specific reason.
- Check that asynchronous failures are awaited and asserted rather than silently swallowed.
- For timeout or deadline assertions, require a forced slow path; use the language-neutral [deadline test guidance](testing-patterns.md#test-anti-patterns) with the repository's runner.
- Distinguish `not run`, `unknown`, and `not covered`; they are different claims.

## Matchers on serialized input

- For each new or changed substring, prefix, or regex matcher on a serialized form (DSN, URL, query string, JSON, header, error text, or log line), identify the key or structural position it is intended to detect.
- Construct at least two concrete inputs: one adversarial input with the pattern inside a value instead of the intended key or position, and one with the pattern in the expected position. For example, a query-key matcher for `mode=` must distinguish `note=mode=admin` from `mode=admin`. Use inputs accepted by the actual format and reachable caller, accounting for decoding or normalization before matching.
- Trace or execute both inputs through the changed matcher and its consumers. Record each input, expected branch, actual branch, and supporting source trace or execution evidence. Report the matcher if either input takes the wrong branch, with the resulting behavior and affected path.
- Never mark a matcher verified from the happy path alone. If either case cannot be verified, retain that limit in the report and name the missing check.

## Classification boundaries

- For each new or changed classification that drives different behavior (such as retryable versus final, decode versus transport error, or 4xx versus 5xx), list concrete inputs on both sides of each boundary and their expected classes under the repository's contract. Trace the resulting behavior, not just the assigned label.
- Include cases where the same error type or message can arise from different causes. For example, `unexpected end of JSON input` can describe a truncated transfer or a complete but malformed body; the shared message alone does not establish the cause.
- Identify the discriminating signal available to the classifier, such as declared length versus bytes received, completion status, HTTP status, or a typed transport error. Where the contract distinguishes transport from decode failures, a body shorter than its applicable declared length belongs on the transport side, while a complete malformed JSON body belongs on the decode side. Derive retryable versus final behavior separately from repository policy. If no reliable signal is available, state the ambiguity and missing evidence instead of assuming the message distinguishes the causes.
- A boundary finding must name the discriminating signal, concrete inputs and expected class on each side, and the actual misclassification. Keep this evidence in the finding so remediation preserves the opposite case instead of simply flipping the classification.

## Invariants under event order

Apply when changed code groups, merges, deduplicates, or assigns ownership to identities, anchors, leases, chains, or equivalent entities. State the promised invariants from the contract, then trace creation-order permutations, concurrent first writes, and entry through a stale or left-behind handle. Track which identity each read and write uses, including conflicting winners and write-once records; a stable key on one path does not prove that all paths converge. Report the concrete order that breaks an invariant, with the normal order as a control.

## Review-fix deltas

- Trigger a review-fix delta when fixes change the behavior of concurrent code, transactions, storage/cleanup, or retries. One delta review covers all fixes of one review round, from the last reviewed head to the new head, not one review per push; intermediate pushes accumulate until the round is ready.
- Pure constant changes (timeout or limit values) without surrounding logic changes, renames, and behavior-preserving moves need no delta review; list them in one line instead.
- Pin the last reviewed head and new head and read only their delta diff plus the functions it touches, not the whole PR again. Map each fix to its finding and decision boundary. If the prior head is unavailable, disclose that the delta cannot be verified and request the missing revision or diff; do not silently substitute a full PR review. Record the new head as reviewed only after completing the round's delta checks.
- Re-review those hunks with the serialized-input matcher and classification-boundary checks above wherever applicable. A small corrective diff still needs both sides checked.
- For each fix, verify the cited scenario and at least one concrete input on the opposite side of every boundary it touched, including different causes that share an error type or message. Record expected and actual branches or classes for both sides; carry forward any unverified side as a verification limit.
- Do not accept a fix merely because it resolves the cited scenario or its new regression test passes. Report a fix that moves the defect to the opposite side, with the discriminating signal and both expected outcomes.

Before/after examples:

| Fixes since the last reviewed head | Before | After |
|---|---|---|
| One round pushes a retry guard, a transaction rollback fix, then a cleanup ownership fix | Three reviews, each re-reading the original PR | One delta from reviewed head A to final head D; read changed hunks and touched functions, checking both sides of changed boundaries |
| Only `timeout = 10` becomes `timeout = 12`, a symbol is renamed, and a helper moves unchanged | Another delta review for mechanical fixes | One line: `No delta review required: timeout constant, rename, behavior-preserving helper move.` |
| A timeout edit also changes the retry condition from `remaining >= cap + reserve` to `remaining >= cap` | Treat the small edit as constant-only | Delta review required: retry logic changed; trace the timeout and the reserved follow-up in the touched function |

## Persisted shortcuts guarded at write time

Apply when the change writes or trusts a persisted shortcut: a stamped attribute, cached ID, memoized decision, coverage journal, watermark, checkpoint, or "already processed" marker used to skip a fallback, recheck, or scan. Also apply when retention, cleanup, or erasure changes the lifetime of the underlying data while the marker survives.

- Trace the full lifetime: write the value while the condition holds, let that condition change through lapse, cancellation, revocation, migration, retention, cleanup, or erasure, then make a better answer or recoverable history available elsewhere. Inspect every read path for revalidation, re-derivation, or invalidation before trusting the shortcut. Check whether deleting covered data also invalidates the marker that claims it exists; preserve any intentional erasure policy when considering re-reads.
- Distinguish "found something" from "found a currently valid answer". A non-empty set of obsolete or canceled records can suppress the fallback even when none satisfies the current requirement.
- If a diff comment or commit message names the hazard the write guard avoids, verify that the guard's protection lasts as long as the persisted value can be read. A correct write-time check alone does not establish lifetime safety. Cite the write, changed condition, shortcut read, and skipped fallback in a candidate; preserve the normal case where the cached answer remains valid.

For example, a saved lookup key selects eligible record A. A later becomes ineligible while replacement B becomes available. A still has non-empty obsolete child records, so a reader treats A as found and never runs the broader lookup that would discover B. Check the invalidation and read-time validation paths before concluding the stale shortcut is reachable.

Regression example: retention drops an old event partition but leaves its interval in a coverage journal. Retention is later raised while the source still offers that history; the rescan subtracts the journal intervals and never restores the missing events. Trace deletion, surviving coverage, and the skipped read. A control that invalidates the deleted interval makes it eligible for collection again.

## Configuration and bootstrap

- Identify application-wide defaults changed alongside a narrow feature. When they can be rolled back independently, recommend a separate atomic commit consistent with repository policy; commit organization alone is not a runtime defect.
- When a diff changes configuration loading or startup, trace the effective value from its supported sources through the framework loader to every changed consumer or writer. Check source selection and precedence, including environment-specific files, overrides, and cached configuration where reachable. Read the installed loader or existing contract tests instead of assuming a direct dotenv parser matches framework bootstrap.
- Distinguish absent, empty, and explicitly supplied values. Check whether a value captured at container creation, image build, or process start shadows a file changed later; writing a file does not update an existing process environment or cache.
- When startup validation guards a runtime check, compare their exact inequalities and effective inputs, including elapsed time, reserves, units, and rounding. Exercise the accepted boundary at runtime; validating a total duration does not establish that the remaining duration can satisfy the same budget.
- For initialization that writes secrets or other durable state, verify that the existence check and writer use the same effective source and target. Trace a normal first start, preservation of existing state, and the highest-risk supported override or restart path. Do not generate or expose real credentials during review.
- Treat removal of a configuration input as a compatibility change. Check existing callers, Compose/CI declarations, documentation, and tests for users supplying that input. Separate a demonstrated break from a maintainer's preference for how optional settings are presented.
- Do not exclude a supported path solely because the environment is for development or the variant was absent from the happy-path fixture. If support or reachability is uncertain, state the evidence needed rather than inventing a defect or assuming safety. Keep this trace scoped to changed behavior; it does not require a deployment matrix or broad framework audit.

Regression example: startup accepts `budget <= handler_deadline`, but each message requires `budget <= handler_deadline - elapsed`. With both configured to 10 seconds and positive setup time, every message is refused. Compare a boundary input with one that leaves sufficient setup margin; merely changing `<=` to `<` need not reserve enough time.

## CI workflows

Load this section only when `.github/workflows/` or other CI configuration changes.

- **Concurrency and event data:** GitHub Actions' default concurrency queue keeps one pending run and replaces it when another arrives, even with `cancel-in-progress: false`. Trace one running run, a pending run, and its replacement. If each carries event-scoped data such as a push's `before..after` range or a payload, identify what the replaced run loses and whether a surviving run reconstructs it. Evaluate `queue: max`, a per-SHA group, or no group against the required serialization and data retention. Verify the target host's support and queue limits before recommending an option; do not bake project-specific availability into this skill. See [GitHub's concurrency semantics](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency).
- **Branch/ref regexes:** Test against actual names from `git branch -r` in the repository under review, mapping remote names to the branch or full-ref form the workflow receives. Include relevant matching and non-matching names; do not validate solely against the author's naming convention. If refs are missing or stale, disclose that evidence limit.
- **Structured payloads:** Trace free-text inputs into JSON or YAML assembled with interpolation, heredocs, or `echo`. Try quotes, newlines, and field-like text to expose invalid serialization or injected fields. Prefer a structured builder such as `jq --arg` or `gh api -f 'key[sub]=value'`, with proper shell quoting, and check the resulting structure locally without sending the payload.
- **Owner verification:** When a proposed fix can only be verified through external side effects, such as `repository_dispatch` to another repository, flag the finding and required verification for the workflow owner. Do not recommend blind edits or trigger the external action as a review probe. State what can be checked locally and what evidence the owner must supply; do not hard-code project-specific ownership here.

## Build and runtime identity

- For configuration written during a build, installation, or privileged setup, trace the writer's user, home directory, configuration scope, and file ownership through to the actual runtime reader. Check user switches, service accounts, changed UID/GID values, and mounted paths where the diff uses them. A successful command as root does not establish that a later unprivileged process sees the setting.
- Verify the effective value as the intended reader, using the real tool's configuration-origin output or a narrow isolated probe when available. Distinguish configuration visibility from permission to read it; do not treat build success or a setup-user assertion as runtime coverage. If the reader cannot be inspected, retain the material assumption as a verification limit.
- Scope trust and permission exceptions to the resources the changed path needs. For example, Git's global configuration belongs to the executing user, while system configuration can serve multiple users; choose deliberately and constrain `safe.directory` to a verified repository path rather than trusting every mounted repository. Do not prescribe system-wide configuration for tools whose contracts differ, and separate an ineffective setting from an independently demonstrated security failure.

## Recoverable failures and process lifetime

- Trace `panic`, assertions, fatal logging, and process exits reached by external input or expected operational failures. Establish whether the failure stops one operation, a worker, or the whole service, and whether callers can still recover.
- Check the actual runtime and framework recovery boundary before claiming a process crash. A raised exception or panic may be caught and translated into the intended response; a fatal exit may bypass that boundary and cleanup.
- Distinguish a recoverable request or dependency failure from a broken internal invariant that makes continued execution unsafe. An intentional fail-stop policy is not a defect without evidence that the condition should be recoverable or the termination violates a reachable contract.

## Locking and callbacks

- Identify the synchronization primitive and its actual semantics. Trace nested calls and callbacks made while a lock is held for reacquisition of the same non-reentrant lock, including indirect calls through another module.
- For every lock, lease, or advisory lock, list values read before acquisition and consumed afterward. Revalidate each under the lock, or prove an immutable/versioned invariant makes reuse safe; serializing the write alone does not refresh its inputs. Compare comments claiming a lock or transaction is held with actual statement order, including helper calls and the transaction handle used.
- Compare acquisition order on reachable overlapping paths when multiple locks are involved. Demonstrate the wait cycle and execution context before reporting a deadlock; different lock order alone is insufficient if the paths cannot overlap.
- Check blocking I/O, waits, and callbacks inside a critical section against the primitive, callback contract, and execution context. Do not forbid all callbacks, timer locks, or blocking operations under every kind of lock.
- Check release and ownership on success, exceptions, early returns, and cancellation. Consider reentrant locks, calls made after unlocking, and established ordering as possible mitigations; prove that the proposed remedy preserves the protected state.

## Concurrent writers of the same rows

- For each table the diff writes, list every writer of its rows or storage, including background retention, cleanup, erasure, rescans, and retries. Search beyond the changed files to identify writers sharing those rows.
- Interleave each pair across read → decide → write. Check that the lock protecting a dependent write also protects its read: for example, read with `FOR UPDATE`, or acquire the shared advisory lock before reading. Verify that all writers participate; a lock acquired only after computing a replacement leaves stale state. An atomic conditional update or version check may instead reject the stale write.
- Trace `SKIP LOCKED` claims against writers that saved an earlier copy. Skipping a currently locked row does not protect a committed claim from a later stale replacement. Include deletion of storage used by in-flight work: identify what happens to pending writes and retries when a partition or equivalent storage disappears.
- Report only with a concrete interleaving: writer identities, the reads and lock boundaries, commit order, and the resulting lost update, resurrected state, or stranded work. Different lock usage alone is insufficient.

Regression examples: a cleanup job reads a pending row without a lock; a worker claims it with `FOR UPDATE SKIP LOCKED` and commits; cleanup then acquires a lock and saves its old copy, undoing the claim. Reading under the shared lock or rejecting a stale version prevents that overwrite. Separately, a worker reads a task targeting partition P; retention drops P; each insert retry targets missing P until attempts run out. Verify coordination with in-flight work or an explicit terminal outcome before claiming the task is stranded.

## Resumable scans and pagination

- Prove each nonterminal iteration advances the cursor without skipping eligible rows. Use the smallest permitted page/work cap and the maximum number of equal sort keys; if ties are unbounded, use more tied rows than fit in one page. Trace the last emitted key, next predicate, and checkpoint after interruption.
- Pin pages to a snapshot or an insertion-monotonic key with a stable tie-breaker. Business timestamps can be preceded by late or backfilled rows. Verify actual insertion/visibility ordering and the scan contract; a generated ID or captured timestamp maximum alone does not prove that later-visible rows cannot fall behind the cursor.

Regression examples: with cap 1, rows A and B share timestamp T; resuming with `timestamp >= T` repeats A forever, while `timestamp > T` loses B. A `(timestamp, unique_key)` cursor handles ties but still misses a later insertion dated before T. A snapshot can cover the initial population; an insertion-ordered continuation must pick up later eligible rows under the supported contract.

## Optimization claims

- Check that a claimed speedup compares a baseline and candidate under comparable workload, build/runtime configuration, dependencies, hardware, and cache or warm-up conditions. Read the supplied measurements before accepting the claim.
- Relate the measured workload to the changed production path. Inspect relevant large-input, contention, or constrained-resource cases when a best-case result could hide a material regression; do not demand every hardware configuration.
- Trace observable results, error behavior, ordering, and resource bounds through an optimization. A speed gain does not justify a correctness or security regression. Do not infer overhead from a wrapper or function call alone without evidence about the actual path.
- Missing or incomparable measurements leave a performance claim unverified; they do not by themselves establish a code defect. Record the missing evidence and a bounded comparison in `Questions` or verification limits. Report a finding only for a concrete failure or grounded contract violation, without universal percentage thresholds. Benchmarks and profiling retain the main skill's approval gate.

## Readability and architecture

- Check whether a new conditional was bolted onto an unrelated flow or whether repeated conditionals reveal a missing model, state, policy, or dispatcher.
- Check whether a refactor actually removes branches or concepts instead of moving the same complexity behind another layer.
- Keep feature-specific logic in the module that owns the concept; do not normalize leakage into shared utilities.
- Search for an existing canonical helper before accepting a near-duplicate.
- Question pass-through wrappers, gratuitous optional types or casts, and abstractions with no demonstrated use.
- When the change creates unreachable or obsolete code, list the exact elements and impact. Do not propose unrelated cleanup.

## Dependencies and lockfiles

- Confirm a new dependency is needed instead of an existing project or standard-library facility.
- Review manifest and lockfile changes together. Check unexpected transitive additions, source or registry changes, install scripts, and hand-edited lockfile patterns.
- For a new or upgraded client on a changed path, read the installed library implementation at the resolved version (module cache, `node_modules`, or equivalent), including the failure paths the caller relies on. Follow deadline cancellation and cleanup, empty or non-JSON error decoding, and error-value truthiness versus HTTP status through to the caller; use the [external-service checks](#external-services-and-fallbacks). Record the version and source locations. If the installed source is unavailable, disclose the unverified contract instead of inferring it from an API name or type.
- For an upgrade, identify behavior and migration risk from repository evidence first. Offer external changelog or advisory research as a high-cost follow-up when it could change the verdict.
- Do not run installs, audits, or lifecycle scripts merely to inspect the diff. Require the normal authorization and cost gate.
- Treat a green install as insufficient evidence; relevant behavior still needs tests.

Regression example: a client deadline expires, then its installed cleanup path interprets a zero cleanup timeout as an unbounded background context. A slow cancellation request holds the caller past its deadline. Trace that branch and configuration; a separately bounded cleanup path is the control. Do not assume zero means disabled or immediate without reading the resolved implementation.

## Web UI and accessibility

- Check native semantics, keyboard reachability, visible focus, form labels and errors, heading order, image alternatives, and focus behavior for dialogs or dynamic content touched by the change.
- For modals with variable content, verify that content and actions remain reachable on short viewports and at zoom: inspect maximum height and scrolling, including long errors, summaries, and narrow-screen wrapping. Compare sibling dialogs in the repository and identify the concrete clipping or unreachable action; a desktop screenshot alone is insufficient.
- Check authorization and validation on the server even when the UI hides or disables an action.
- Treat automated accessibility tools, browser audits, screen-reader passes, screenshots, and visual regression suites as high-cost follow-ups unless the user already requested them.

## Queues and retrying workers

- Derive acknowledgement and retry semantics from the actual queue framework and repository policy.
- Distinguish malformed messages that should be discarded or dead-lettered from transient processing failures that should retry.
- Check whether a swallowed error can acknowledge incomplete work.
- Verify idempotency under redelivery and concurrent delivery for the same entity.
- Check retry limits, poison-message handling, visibility or lease renewal, and partial side effects.

Do not assume one platform's convention, such as returning `nil` or an error, applies to another worker runtime.

## Multi-system writes

- Trace database, queue, cache, and external API effects in execution order.
- At every failure boundary, determine whether state rolls back, remains intentionally partial, or converges through an idempotent retry. After committed effects, treat the hand-off, compensation, or escalation itself as fallible: trace its error branch through the caller. Logging and returning a handled/stop result can abandon incomplete work; verify that failure reaches a retrying or alerting path.
- Trace every refusal or early return, including a disabled feature flag, validation failure, conflict, or 503/409 response, and list side effects already committed before it. Irreversible request effects, including identity pins, external calls, and durable inserts, must follow every refusal decision for that request. A refusal after committing such an effect is a defect; identify both, distinguishing unrelated audit records from the requested effect.
- On resume/retry paths, trace every operation argument sent to an external call to the persisted record. New request values must not replace the recorded subject, owner, destination, or other operation input; a stale entry handle can now identify a different entity. If an argument is derived, prove the derivation uses the persisted record.
- An optional or side path placed before the primary call on a request path must preserve the caller's deadline for the primary operation. Trace its maximum wait, retries, and cancellation/cleanup; a best-effort label or swallowed error does not bound how much of the caller's budget it consumes.
- Look for orphaned records, published events for rolled-back data, dangling references, and retries that duplicate completed steps.
- Verify that readers cannot observe an invalid intermediate state when operations overlap.

Regression examples: an endpoint commits a new record, then checks a disabled feature flag and returns 503; the caller sees refusal although the write survives. Move the refusal ahead of the mutation or prove rollback before returning it. Separately, optional enrichment waits out the shared deadline before invoking the primary operation, so that operation always starts canceled on the slow path. Check that skipping or bounding enrichment actually preserves the primary operation's required budget.

Regression example: response composition moves after a handler has changed an account and buffered its reply. Composition fails, then the escalation call fails too; its helper only logs and returns a handled sentinel. The caller discards the buffered reply and skips its processing-error fallback, leaving neither a reply nor an escalation. Force both failures and trace the returned status into the caller; the clean control propagates the escalation error to recovery and reserves the handled result for successful escalation.

## Dependency injection and registries

- Compare new bindings with the repository's established container or registry pattern.
- Search all implementations and consumers before claiming a missing or duplicate binding.
- Verify interface-to-concrete registration, lifecycle ownership, and test replacement behavior.
- Treat framework-specific constructs as evidence only after reading nearby working registrations.

## External services and fallbacks

- Separate expected absence from timeouts, authentication failures, malformed responses, and service outages.
- When a fallback returns the caller's own input (return the resolved value if present, otherwise the input), follow later equality and ownership checks against that input. On the fallback branch they are vacuous unless provenance is preserved and checked: fallback equality proves no resolution or ownership. Trace an unresolved input and a genuinely resolved equal value as separate cases.
- Require unexpected fallback paths to remain observable according to repository logging policy.
- Check empty successful responses as well as empty and non-JSON error bodies. For a new or upgraded client, inspect the [installed failure paths](#dependencies-and-lockfiles): establish whether failure is signaled by a thrown exception, a returned error value, or HTTP status. A falsey error value does not establish a successful status; trace decoding exceptions and cancellation/cleanup through the caller's fallback and deadline handling.
- Verify that logs and metrics contain operation and entity metadata without raw user content, credentials, prompts, payment data, or response bodies.
- Confirm metric names match their expressions, units, cardinality, and boolean polarity.
- Treat model or tool output as untrusted input; check permission enforcement, output validation, and token, rate, and loop bounds.

Regression example: an installed client returns a non-2xx response with an absent or empty-string error for an empty body; `if error` falls through to success. A non-JSON proxy error can instead throw during decoding and bypass the intended error branch. Trace both responses alongside a valid 2xx control, checking status and the installed decoder's actual result rather than assuming all failures carry a truthy structured error.

## Provenance

Selected recoverable-failure, locking, and comparative-measurement topics are
adapted and rewritten from [Mte90/linus-torvalds-skill at commit
`97625cb16eaa6061e02832a33ccf56440252d41f`](https://github.com/Mte90/linus-torvalds-skill/blob/97625cb16eaa6061e02832a33ccf56440252d41f/linus-torvalds-skill/SKILL.md),
published under [CC0-1.0](https://github.com/Mte90/linus-torvalds-skill/blob/97625cb16eaa6061e02832a33ccf56440252d41f/LICENSE).
The repository's evidence, severity, scope, and approval rules govern these checks.
