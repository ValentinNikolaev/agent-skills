# Conditional Review Checks

Read only the sections that match the changed languages or change patterns.

## Contents

- [Tests and verification](#tests-and-verification)
- [Readability and architecture](#readability-and-architecture)
- [Dependencies and lockfiles](#dependencies-and-lockfiles)
- [Web UI and accessibility](#web-ui-and-accessibility)
- [Go](#go)
- [Queues and retrying workers](#queues-and-retrying-workers)
- [Multi-system writes](#multi-system-writes)
- [Dependency injection and registries](#dependency-injection-and-registries)
- [External services and fallbacks](#external-services-and-fallbacks)

## Tests and verification

- Prefer behavior assertions over implementation-detail assertions that break during safe refactors.
- For a bug fix, identify the regression test that fails without the fix and passes with it; if absent, name the exact missing scenario.
- Check happy path, the highest-risk edge case, and meaningful error or partial-failure behavior introduced by the change.
- Mock system boundaries such as databases, clocks, filesystems, and remote services; do not mock the business logic under test without a repository-specific reason.
- Check that asynchronous failures are awaited and asserted rather than silently swallowed.
- Distinguish `not run`, `unknown`, and `not covered`; they are different claims.

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

## Go

- Read `go.mod` before applying version-specific language or standard-library rules.
- Check asymmetric nil handling: guarding or logging pointer presence at one access and dereferencing the same value later without a guard.
- Verify goroutine exit conditions, wait semantics, channel ownership, closure, mutex coverage, and deferred unlocks.
- When a test claims complete registry or map coverage, require an existence check such as `value, ok := registry[key]`; a zero value from naked indexing does not prove the key exists.
- Check error wrapping against local conventions. Do not require wrapping when a sentinel identity or established boundary intentionally needs the original error.
- When method signatures or interfaces change, search implementations, consumers, dependency wiring, mocks, and expectations.

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
