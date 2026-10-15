# Python Review Checks

Apply only to changed Python behavior and nearby tests. Read `pyproject.toml`, supported Python versions, dependency constraints or lockfiles, CI commands, and the relevant framework configuration. Use the repository's actual runner and environment; do not assume pytest, asyncio, Pydantic, Django, FastAPI, uv, or Poetry.

Selected topics are adapted from awesome-skills/code-review-skill at commit `4850184dfd7765ea7b3c5c4e9b6cf8e0815ee7cb`, `reference/python.md`; see `LICENSE.awesome-skills` in this package. Repository-specific evidence and scope rules take precedence.

## Values and contracts

- Trace mutable defaults, mutable class attributes, shallow copies, cached values, and aliases between callers. Demonstrate unwanted sharing across calls or instances; intentional shared state is not itself a defect.
- Check late-bound loop variables in callbacks and deferred work. Distinguish a callback invoked immediately from one invoked after the loop advances.
- Distinguish `None`, empty values, zero, and missing keys according to the contract. Check identity versus equality only when a reachable value changes the result.
- Trace generator consumption, lazy exceptions, one-shot iterators, and lifetime of resources supplying streamed data. An annotation such as `Iterable` does not promise repeatable iteration.
- Treat type annotations, `TypedDict`, casts, and dataclasses as separate from runtime input validation. Check the actual validator, coercion policy, and error handling at JSON, environment, database, CLI, or external-service boundaries.
- Check syntax, standard-library APIs, and annotation evaluation against the minimum supported interpreter. Do not demand modern syntax that would break a supported runtime or introduce typing abstractions without a concrete benefit.

## Async, concurrency, and resources

- Identify who owns each coroutine, task, thread, process, queue, and connection; trace completion, exceptions, shutdown, and bounded concurrency. A bare coroutine call does not schedule work, and creating a task does not prove its result is observed.
- Check blocking I/O and CPU work on the actual execution path. Offloading to a thread needs a thread-safe dependency and does not make already-running work cancellable; do not require an async rewrite for synchronous code.
- Follow cancellation and timeouts through callers and cleanup. Preserve cancellation propagation after cleanup unless the repository deliberately defines suppression. Do not claim `except Exception` catches `asyncio.CancelledError` on modern Python: it derives from `BaseException`.
- Distinguish `asyncio.gather` failure behavior from `TaskGroup` sibling cancellation. Check supported Python versions before suggesting `TaskGroup`; do not replace one with the other without checking partial-result semantics.
- Check queue acknowledgement and worker termination on success, failure, cancellation, and exhausted input. A bounded queue alone does not bound the number of tasks created around it.
- Check context managers, `finally`, transaction ownership, temporary files, and generator close paths. A returned stream must not depend on a resource already closed by its producer.
- For shared state, verify synchronization and the actual interpreter/build and library guarantees. Do not infer race freedom from the GIL or one passing test. Treat process-pool startup and serialization assumptions as platform-dependent.

## Exceptions and security

- Follow errors to the caller boundary. Distinguish an intentional fallback from swallowed failures, partial success reported as complete, and exception translation that loses actionable context. Preserve causes when needed without exposing secrets.
- Trace untrusted input into subprocess arguments, shell text, SQL, templates, file paths, dynamic imports, and deserializers. `shell=False` still requires checking executable choice and argument/option injection; `pickle` is not a safe format for untrusted data.
- For filesystem operations, verify resolved scope, traversal and symlink behavior, encoding, and atomicity when relevant. Check logs and exception messages for credentials and user content.
- Treat importing configuration or a module as executable code. Do not import an untrusted project merely to inspect settings or annotations.

## Tests and verification

- Use pytest, unittest, or another runner only as configured. Check test collection, selected cases, skip reasons, and assertions that distinguish the changed behavior. A green run with no relevant tests is unrun evidence for that behavior.
- For async tests and fixtures, inspect the installed plugin and its mode, event-loop scope, decorators, and teardown. Do not assume that an async function is awaited because its name starts with `test_`.
- Patch the name looked up by the code under test, use async-aware doubles at async boundaries, and verify meaningful calls/results without mocking away the behavior being reviewed.
- Check fixture scopes and cleanup, clock/randomness control, environment restoration, and shared caches. Do not mandate parameterization, pytest, a coverage percentage, or a particular assertion library.
- Run only configured, targeted checks when useful. Ruff, mypy, and Pyright are conditional tools, not installation requirements. Type-check success does not validate runtime input; a skipped checker is not a pass.
- Use the main review's proportional negative-control rule for regression claims. Broad profiling, coverage generation, dependency scans, and mutation campaigns remain separate costly checks.

Primary references: [Python asyncio tasks](https://docs.python.org/3/library/asyncio-task.html), [unittest.mock: where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch), [pytest-asyncio modes](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html).
