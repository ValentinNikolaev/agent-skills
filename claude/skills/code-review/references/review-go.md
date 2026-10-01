# Go Review Checks

Apply these checks only to changed Go behavior and nearby tests. The repository's `AGENTS.md`, `go.mod`, Go version, and established error and test conventions take precedence. Report a finding only after tracing a concrete failure path through the changed code.

## Production code

- Trace pointer and interface values from creation to use. A nil guard on one access does not protect a later dereference; distinguish a nil interface from an interface holding a typed nil when relevant.
- Follow errors through the caller boundary. Check whether errors are dropped, mislabeled, wrapped in a way that loses required identity, or converted into apparent success. Use `errors.Is` and `errors.As` only where the project exposes matching or typed-error contracts.
- For goroutines, identify the owner, exit condition, context cancellation, waits, and what happens when a caller returns early. For channels, identify who sends, receives, and closes; do not propose closing from a non-owner merely to quiet a leak.
- For shared state, inspect all relevant accesses and synchronization, including tests. A passing non-race test does not establish race freedom.
- On changed interfaces or method signatures, search implementations, callers, registrations, mocks, and generated interfaces before declaring them updated or broken.
- Check map lookups that purport to prove membership: the zero value alone is insufficient when the `ok` result matters.

## Tests

- Read the package's test runner and existing conventions before judging table-driven tests, subtests, fixtures, or test doubles. Do not require a table for a single meaningful case.
- Check that each case asserts the behavior it names, including the error path and a discriminating observable. For bug fixes, identify whether the assertion would fail before the fix; use the main skill's proportional negative-control rule.
- Do not demand `t.Parallel` by default. When it is used, check for shared fixtures, mutable globals, and process-wide changes. `t.Setenv` and `t.Chdir` cannot run in a parallel test or below a parallel ancestor.
- Keep `t.Fatal` and `t.FailNow` in the test goroutine. For HTTP handlers or background goroutines, return an error through a channel or another observable the test can assert.
- For HTTP adapter tests, inspect the request actually sent and the response/error contract. `httptest` may test the boundary without calling a live service; label skipped integration work as unrun, not passed.
- When a test claims all registry entries or cases are covered, verify membership and counts instead of accepting zero values or vacuous loops.

## Verification

Prefer the repository's narrow package test command. Suggest a targeted race-detector run when changed concurrency creates a plausible race and the environment supports it; it has substantial runtime cost and only observes paths executed by the test. Do not infer race freedom from one green run.

Go references: [testing package](https://pkg.go.dev/testing), [race detector](https://go.dev/doc/articles/race_detector).
