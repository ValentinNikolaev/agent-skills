# Conditional Review Checks

Read only the sections that match the changed languages or infrastructure.

## Contents

- [Go](#go)
- [Queues and retrying workers](#queues-and-retrying-workers)
- [Multi-system writes](#multi-system-writes)
- [Dependency injection and registries](#dependency-injection-and-registries)
- [External services and fallbacks](#external-services-and-fallbacks)

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
