# FastAPI Review Checks

Apply only to changed FastAPI behavior and its callers/tests. Read the owning Python constraints, resolved FastAPI, Starlette and Pydantic versions, app lifespan, dependency overrides, and test configuration. Continue using the main review's evidence, severity, scope, and cost rules. Do not install a framework, migrate Pydantic, start a server, or enable telemetry to review a diff.

This reference adapts and substantially rewrites the official FastAPI skill and its dependency, response, streaming, and model references at commit `0b919816378eaa773df7ce4204414c712c9fdbea`; see `LICENSE.fastapi`. It adds repository-specific review and version boundaries. Upstream preferences are not universal correctness rules.

## Public inputs and outputs

- Trace body, path, query, header and dependency values through validation to use. A type annotation alone does not validate data outside FastAPI's validation boundary. Separate optional values, missing values, coercion and strict validation according to the public contract and installed Pydantic version.
- Check the actual response path: return annotation, explicit `response_model`, include/exclude options, aliases, serializers, and direct `Response` objects. An internal model can expose secrets if it becomes the public schema. A direct response may bypass model filtering; test the emitted body, not just the DTO.
- Review status codes, content types, errors and OpenAPI against the promised API. A changed model can break consumers even when the endpoint still returns 200. Inspect representative calls before claiming compatibility.
- Prefer `Annotated` for new declarations where supported, but do not report working `Depends(...)` defaults, ellipsis, `RootModel`, class dependencies, or an existing ORM as bugs solely because newer guidance prefers another form. Establish an actual failure or binding repository rule.

## Dependencies and lifetime

- Trace authorization through the actual dependency graph, router/app dependencies and overrides. Router-level registration does not prove that every route or alternate entry point is protected. Verify that test overrides are restored.
- For each `yield` dependency, identify when its cleanup occurs relative to serialization, streamed consumption and background work. Check the installed version's `scope` behavior; a stream must not use a session or file after cleanup. Moving cleanup later can also retain scarce connections for slow clients.
- Give background tasks and lifespan resources explicit ownership, failure observation and shutdown. Request-scoped objects are not automatically safe to capture for later work. Do not assume in-process background tasks provide durable delivery or retries.

## Async and streaming

- Trace blocking HTTP/DB/file work inside `async def` endpoints and dependencies. A regular `def` endpoint may be intentionally delegated to a threadpool; calling a synchronous helper directly from an async function is a different path. Check thread safety and bounds before recommending offloading.
- Distinguish bytes, JSON Lines and SSE framing, MIME types and serialization. Verify support before recommending native `EventSourceResponse`, `ServerSentEvent`, frontend helpers or telemetry APIs from a newer FastAPI release. Do not substitute a different streaming protocol because an example uses it.
- Test the resource lifetime while chunks are consumed, including client disconnect, cancellation and producer failure. A test that buffers the whole body may not exercise incremental delivery, disconnect handling, proxy buffering or backpressure. State those limits.
- Distinguish active concurrent operations, created tasks, queued items and retained response bodies. A semaphore alone does not bound all pending work or impose a requests-per-second limit.

## Verification

Use the configured local ASGI test setup and targeted checks. Check public JSON filtering, invalid input, authentication/authorization, error paths, dependency cleanup and lifespan as relevant. A test using dependency overrides does not establish the real dependency's behavior. Keep OpenAPI/schema checks distinct from HTTP behavior and real streaming evidence. Report missing packages, unsupported features, skipped tests and untested deployment behavior explicitly.

Primary sources: [FastAPI response models](https://fastapi.tiangolo.com/tutorial/response-model/), [dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/), [async guidance](https://fastapi.tiangolo.com/async/), and [Pydantic RootModel](https://docs.pydantic.dev/latest/api/root_model/).
