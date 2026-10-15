# Cobra and Viper Console Contracts

Apply only to an identified Cobra/Viper project. These libraries are optional implementation choices, not prerequisites for a good console interface. Use the parent skill for the command/output/automation contract and `code-review` for a report-only diff review.

## State and execution

- Build fresh command and configuration instances for independent invocations when mutable global flags/config would leak state. Pass typed configuration into business logic rather than requiring the domain to depend on the CLI framework.
- Define error propagation and printing once at the boundary. With error-returning handlers, distinguish invalid arguments from runtime failures and check whether inherited hooks, usage output, and error output preserve the desired exit/stream contract.
- Route successful machine output and diagnostics to the specified streams. Use the command's injectable writers/input for testing rather than bypassing them with process-global output.
- Propagate cancellation through execution and long-running operations. Specify what partial output and exit status remain on cancellation.

## Configuration

- Establish which flags are local or inherited and resolve collisions from the actual command tree. Define precedence, environment names, defaults, validation, and whether a config file is optional; missing required config must not silently become valid defaults.
- With Viper struct unmarshaling, register keys through defaults or explicit bindings as needed. `AutomaticEnv` alone does not make every environment-only struct field discoverable.
- Prefer isolated Viper instances for independent runs/tests. If hot reload exists, validate the new configuration and its publication to concurrent readers; do not mutate shared state without an ownership/synchronization contract.
- Keep secrets out of help defaults, echoed arguments, config dumps, and diagnostic output.

## Acceptance evidence

Exercise the real root-to-subcommand path with injected arguments, input, output, and dependencies. Include configuration precedence, argument failures, runtime failures, repeated invocation isolation, and cancellation only where relevant. A test that invokes a leaf handler directly does not verify registration, parsing, or inherited hooks. Preserve local test conventions instead of requiring assertion libraries or banning them.

Adapted from [spf13/cobra-viper](https://github.com/spf13/go-skills/blob/9ac6eca43161163bb21621a520a57df50d5ad464/cobra-viper/SKILL.md) and selected [Samber CLI/Cobra/Viper guidance](https://github.com/samber/cc-skills-golang/tree/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717/skills/golang-cli), under the parent package's scoped MIT licenses. Automatic library recommendations, installation, and corporate layout rules are omitted.
