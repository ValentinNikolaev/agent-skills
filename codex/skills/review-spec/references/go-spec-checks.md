# Go Specification Checks

Use these checks for a proposed Go design, not as a second code review or an implementation plan. Read the project's `go.mod`, toolchain policy, existing contracts, and architecture decisions before applying an idiom.

## Contracts and failure paths

- Identify consumers of proposed interfaces and the capability each consumer needs. Prefer a concrete type or small consumer-owned interface when it meets the requirement, but do not reject an established abstraction solely because it has one current implementation.
- Specify error outcomes, caller-visible error identity, partial results, and retry/idempotency behavior where they affect the contract. Do not require exposing an internal database or transport error merely to use `%w`.
- State ownership and cleanup for connections, streams, files, transactions, and background work. Specify cancellation, shutdown, outstanding work, and the bound on fan-out or queued input when relevant.
- Check that proposed APIs exist in the supported Go version. `WaitGroup.Go` does not itself bound concurrency or propagate errors. Separate a toolchain upgrade decision from the proposed feature.
- Evaluate package dependencies and reuse against actual responsibilities. `internal/`, nested packages, worker pools, generics, and architectural styles are not defects by name; identify a concrete dependency, lifecycle, or complexity cost.

## Cobra and Viper, only when used

- Identify where new commands are registered and how command state is isolated between invocations and tests. Factory construction is useful when mutable global commands would leak state; a mandatory rewrite of unrelated commands is not a spec requirement.
- Distinguish syntax/argument failures from runtime failures. Specify error propagation, exit status, output streams, and cancellation rather than requiring a particular handler method without examining its behavior.
- Specify flag/config/environment precedence and required versus optional configuration. If Viper unmarshals a struct, ensure environment-only keys are registered with defaults or explicit bindings; `AutomaticEnv` alone does not guarantee discovery of every struct field.
- For file-writing commands, address equal input/output targets, overwrite rules, partial output, and cleanup where data loss is possible.
- Require observable acceptance cases for parsing, configuration, errors, and cancellation. Exercise the real root-to-subcommand path when registration or inherited hooks matter.

## Report

Tie every concern to a spec section and its consequence. Keep harmless preferences out of blockers; put unresolved material assumptions in Questions. Use the parent skill's `READY`, `REVISE`, or `BLOCKED` verdict. Do not edit the spec, invoke subagents automatically, or add implementation details the design deliberately leaves open.

Adapted and substantially rewritten from [spf13/go-spec-reviewer](https://github.com/spf13/go-skills/blob/9ac6eca43161163bb21621a520a57df50d5ad464/go-spec-reviewer/SKILL.md), under the bundled `LICENSE.spf13-go-skills`. Host-specific paths, automatic delegation, and universal architecture prescriptions are omitted.
