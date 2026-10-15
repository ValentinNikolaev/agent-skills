# Claude SDK Contracts

Modified adaptation of Anthropic's Python/TypeScript Claude API and tool-use references at commit `dbd4588f9e1033efb41dad4bef2f7947c8993d44`. This file adds version checks, helper/wire distinctions and independent security/verification requirements. See `LICENSE.anthropic-skills` and `NOTICE.anthropic-skills`.

## Choose the product before choosing code

| Surface | Ownership and appropriate result |
| --- | --- |
| Messages API call | The application sends a request and handles its response, streaming, schema and error contract |
| API SDK Tool Runner | SDK supplies a loop for custom tools; the application hosts execution, permissions and deployment |
| Manual Messages tool loop | Application owns loop control and tool execution; preserve protocol IDs/content and bounded failure handling |
| Managed Agents | Anthropic-managed loop with a cloud or explicitly configured self-hosted environment; verify platform availability and provisioning/data scope |
| Claude Agent SDK | Separate Claude Code harness library with built-in tools; the developer still owns deployment. Outside this skill's authoring scope |

A loop helper is not a security sandbox. An SDK package, an HTTP API resource and a deployed container are different objects. Do not infer file access, isolation or managed hosting from the word agent.

## Python and TypeScript binding evidence

| Concern | Python | TypeScript |
| --- | --- | --- |
| Regular API SDK | `anthropic` | `@anthropic-ai/sdk` |
| Agent SDK, separate package | `claude-agent-sdk` | `@anthropic-ai/claude-agent-sdk` |
| Call shape | Keyword arguments; inspect sync/async client and returned type | Object parameters; inspect declarations, promises and stream types |
| Typed output | Pydantic/SDK helper as supported by the installed version | SDK schema helpers and installed validation-library version |
| Tool Runner | Verify the installed runner/decorator namespace and sync/async behavior | Verify the installed runner/helper namespace and schema-library compatibility |

Inspect lockfile selection, including workspace overrides and duplicate package versions. Use project commands for compilation/type checking; a transpile-only TypeScript test does not check declarations. Do not import an untrusted project to discover its configuration. Read installed metadata/declarations before executing anything.

## Structured output and tool input

The Messages wire shape uses `output_config.format` for schema-constrained JSON output. The Python `messages.parse` helper can accept a model via a parameter named `output_format` and translate it to the wire shape. Verify the exact installed helper; a blanket textual rename can break correct code.

`strict: true` concerns tool-name/input schema compliance. Check supported JSON Schema constructs and SDK schema transformation; retain local validation for constraints that the backend schema cannot express. Decide output formatting and tool validation independently according to the contract.

After generation, handle refusal, truncation and other non-success stop conditions before trusting a parsed result. Typed output can still violate business policy. Do not replace native schema support with regex extraction or repair prompts merely because those are familiar. Plain text, intentional manual parsing and an older compatible integration remain valid when schema-constrained output is not required or supported.

For streamed tool input, treat accumulated partial JSON as incomplete until the relevant tool block is complete and validation succeeds. Validate again where an operation executes; a tool name/description does not grant authority. Reject unknown tools and correlate every result with the correct call ID. Do not turn tool exceptions into apparent successful results.

## Verification layers

| Evidence | Establishes | Does not establish |
| --- | --- | --- |
| Manifest and lockfile | Selected package/runtime constraints | Actual import resolution or remote behavior |
| SDK declarations/signatures | Available local methods and parameter shapes | Server/model/platform feature support |
| Offline request/response fixtures | Client serialization, error handling and validation | Live acceptance, billing or sandbox isolation |
| Authorized live API probe | The observed platform/model accepted that specific request | All supported versions, all tools or complete security |

Use deliberately malformed inputs, refusal/truncation responses, unknown tool names, duplicate/retried calls, and cancelled streams as applicable. Keep test expectations independent of the request-builder implementation. Record test selection and skips; a stubbed success alone is not a successful integration.

Do not freeze model IDs, prices, beta headers or availability tables in this workflow. Refresh those facts from the relevant primary source when they affect the task, and record what version/platform the evidence describes.
