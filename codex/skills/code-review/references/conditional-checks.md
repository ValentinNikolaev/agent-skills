# Conditional Review Checks

Read only the sections that match the changed languages or change patterns.

## Contents

- [Tests and verification](#tests-and-verification)
- [Configuration and bootstrap](#configuration-and-bootstrap)
- [Recoverable failures and process lifetime](#recoverable-failures-and-process-lifetime)
- [Locking and callbacks](#locking-and-callbacks)
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
- For a bug fix, identify the regression test that fails without the fix and passes with it; if absent, name the exact missing scenario.
- Check happy path, the highest-risk edge case, and meaningful error or partial-failure behavior introduced by the change.
- Mock system boundaries such as databases, clocks, filesystems, and remote services; do not mock the business logic under test without a repository-specific reason.
- Check that asynchronous failures are awaited and asserted rather than silently swallowed.
- Distinguish `not run`, `unknown`, and `not covered`; they are different claims.

## Configuration and bootstrap

- Identify application-wide defaults changed alongside a narrow feature. When they can be rolled back independently, recommend a separate atomic commit consistent with repository policy; commit organization alone is not a runtime defect.
- When a diff changes configuration loading or startup, trace the effective value from its supported sources through the framework loader to every changed consumer or writer. Check source selection and precedence, including environment-specific files, overrides, and cached configuration where reachable. Read the installed loader or existing contract tests instead of assuming a direct dotenv parser matches framework bootstrap.
- Distinguish absent, empty, and explicitly supplied values. Check whether a value captured at container creation, image build, or process start shadows a file changed later; writing a file does not update an existing process environment or cache.
- For initialization that writes secrets or other durable state, verify that the existence check and writer use the same effective source and target. Trace a normal first start, preservation of existing state, and the highest-risk supported override or restart path. Do not generate or expose real credentials during review.
- Treat removal of a configuration input as a compatibility change. Check existing callers, Compose/CI declarations, documentation, and tests for users supplying that input. Separate a demonstrated break from a maintainer's preference for how optional settings are presented.
- Do not exclude a supported path solely because the environment is for development or the variant was absent from the happy-path fixture. If support or reachability is uncertain, state the evidence needed rather than inventing a defect or assuming safety. Keep this trace scoped to changed behavior; it does not require a deployment matrix or broad framework audit.

## Recoverable failures and process lifetime

- Trace `panic`, assertions, fatal logging, and process exits reached by external input or expected operational failures. Establish whether the failure stops one operation, a worker, or the whole service, and whether callers can still recover.
- Check the actual runtime and framework recovery boundary before claiming a process crash. A raised exception or panic may be caught and translated into the intended response; a fatal exit may bypass that boundary and cleanup.
- Distinguish a recoverable request or dependency failure from a broken internal invariant that makes continued execution unsafe. An intentional fail-stop policy is not a defect without evidence that the condition should be recoverable or the termination violates a reachable contract.

## Locking and callbacks

- Identify the synchronization primitive and its actual semantics. Trace nested calls and callbacks made while a lock is held for reacquisition of the same non-reentrant lock, including indirect calls through another module.
- Compare acquisition order on reachable overlapping paths when multiple locks are involved. Demonstrate the wait cycle and execution context before reporting a deadlock; different lock order alone is insufficient if the paths cannot overlap.
- Check blocking I/O, waits, and callbacks inside a critical section against the primitive, callback contract, and execution context. Do not forbid all callbacks, timer locks, or blocking operations under every kind of lock.
- Check release and ownership on success, exceptions, early returns, and cancellation. Consider reentrant locks, calls made after unlocking, and established ordering as possible mitigations; prove that the proposed remedy preserves the protected state.

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
- For an upgrade, identify behavior and migration risk from repository evidence first. Offer external changelog or advisory research as a high-cost follow-up when it could change the verdict.
- Do not run installs, audits, or lifecycle scripts merely to inspect the diff. Require the normal authorization and cost gate.
- Treat a green install as insufficient evidence; relevant behavior still needs tests.

## Web UI and accessibility

- Check native semantics, keyboard reachability, visible focus, form labels and errors, heading order, image alternatives, and focus behavior for dialogs or dynamic content touched by the change.
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
- At every failure boundary, determine whether state rolls back, remains intentionally partial, or converges through an idempotent retry.
- Look for orphaned records, published events for rolled-back data, dangling references, and retries that duplicate completed steps.
- Verify that readers cannot observe an invalid intermediate state when operations overlap.

## Dependency injection and registries

- Compare new bindings with the repository's established container or registry pattern.
- Search all implementations and consumers before claiming a missing or duplicate binding.
- Verify interface-to-concrete registration, lifecycle ownership, and test replacement behavior.
- Treat framework-specific constructs as evidence only after reading nearby working registrations.

## External services and fallbacks

- Separate expected absence from timeouts, authentication failures, malformed responses, and service outages.
- Require unexpected fallback paths to remain observable according to repository logging policy.
- Check empty successful responses as well as explicit errors.
- Verify that logs and metrics contain operation and entity metadata without raw user content, credentials, prompts, payment data, or response bodies.
- Confirm metric names match their expressions, units, cardinality, and boolean polarity.
- Treat model or tool output as untrusted input; check permission enforcement, output validation, and token, rate, and loop bounds.

## Provenance

Selected recoverable-failure, locking, and comparative-measurement topics are
adapted and rewritten from [Mte90/linus-torvalds-skill at commit
`97625cb16eaa6061e02832a33ccf56440252d41f`](https://github.com/Mte90/linus-torvalds-skill/blob/97625cb16eaa6061e02832a33ccf56440252d41f/linus-torvalds-skill/SKILL.md),
published under [CC0-1.0](https://github.com/Mte90/linus-torvalds-skill/blob/97625cb16eaa6061e02832a33ccf56440252d41f/LICENSE).
The repository's evidence, severity, scope, and approval rules govern these checks.
