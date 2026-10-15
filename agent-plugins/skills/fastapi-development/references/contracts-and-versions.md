# FastAPI Contracts and Version Gates

Read only the feature under change. The upstream snapshot is guidance, not proof that the project's installed release exposes every API.

## Compatibility evidence

Record the minimum supported Python, resolved FastAPI, Starlette, Pydantic and relevant test-client versions. Read lockfiles and project configuration before suggesting syntax or new dependencies. When checking local package metadata, avoid executing an untrusted project's configuration just to discover a version.

| Feature | Evidence required before use |
| --- | --- |
| `Annotated` declarations | Supported interpreter/import path and FastAPI's parameter/dependency interpretation |
| Pydantic validation/serialization | Installed major version, config, aliases, validators and public schema behavior |
| `Depends(..., scope=...)` | Installed signature and cleanup timing, especially for a streamed response |
| Native `fastapi.sse` and `EventSourceResponse` | Installed exports, accepted event shape, serialization and cancellation behavior |
| Yield-based JSON Lines or bytes | Installed endpoint/response handling; test actual framing and content type |
| `app.frontend()` / `router.frontend()` | Installed API, route precedence, static root and fallback behavior |
| Native OpenTelemetry setup | Installed support, required extras, explicit exporter/configuration intent and sensitive data policy |

If a feature is absent, use the established supported implementation. An upgrade is a separate compatibility decision; do not silently raise the version floor to match upstream examples.

## Request and response boundaries

Prefer plain required fields without `...` in new models. A nullable field and an optional field are not automatically the same contract. Use explicit defaults where omission is intended, matching the installed Pydantic version.

Prefer `Annotated` for reusable dependency and parameter metadata when compatible. Preserve callable behavior outside FastAPI and do not add aliases with no reuse or clarity benefit.

Choose the public response type independently from internal persistence objects. A return annotation or `response_model` can validate and filter a normal returned object; manually returning a response object follows another path. Test that internal fields are absent from the serialized body. Check alias/default/exclusion behavior as well as OpenAPI.

`RootModel` remains a Pydantic API. Prefer a direct validated annotation where it expresses the FastAPI boundary simply; retain a wrapper when it supplies a needed public abstraction or behavior. This is not permission to rewrite working consumers.

## Ownership and streaming

For a `yield` dependency, mark acquisition, handler execution, serialization, stream consumption and release. Confirm the installed version's default and explicit scopes. A file/session closed before iteration is a defect; retaining it until a slow client completes can exhaust a pool. Choose ownership according to the actual resource use.

Give lifespan resources a startup/shutdown owner. Separate request completion from durable background processing. In-process background work can be interrupted and does not establish queue delivery guarantees.

| Output | Verify |
| --- | --- |
| Normal JSON | Public filtering, aliases, validation failure and error/status behavior |
| JSON Lines | Each record's serialization and delimiter; no accidental single JSON array |
| SSE | Event framing, content type, data encoding, disconnect and generator cleanup |
| Bytes | Content type, byte iteration and resource close on completion/failure |

Use a local iterator probe to establish producer lifetime, an ASGI test for HTTP integration, and an appropriate streaming client/deployment probe only when that stronger claim is needed and authorized. Do not label these three forms of evidence interchangeable.

## Tools and references

Use configured tools and repository commands. Do not replace SQLAlchemy with SQLModel, Requests with HTTPX, or asyncio/AnyIO with Asyncer solely to follow a preference. Lint formatting, type checking, runtime validation and authorization are separate properties.

Official references: [response models](https://fastapi.tiangolo.com/tutorial/response-model/), [yield dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/), [async](https://fastapi.tiangolo.com/async/), [testing](https://fastapi.tiangolo.com/tutorial/testing/), and [Pydantic RootModel](https://docs.pydantic.dev/latest/api/root_model/). Consult release-matched sources for newer helpers.

Adapted from the official FastAPI skill and references at commit `0b919816378eaa773df7ce4204414c712c9fdbea`, with additional compatibility and verification boundaries. See `LICENSE.fastapi`.
