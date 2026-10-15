<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# PHP Compatibility and Tool Boundaries

Adapted and substantially rewritten from Netresearch DTT GmbH's PHP modernization skill at commit `8df68546e8d9fa00e4530e9c26e73adcc3322834`, especially migration, type-safety, immutability, and tooling topics. Distributed under CC-BY-SA-4.0; see the package license and notice. Verify technical claims against installed versions and primary documentation.

## Runtime and package compatibility

- Reconcile `require.php`, `config.platform.php`, actual PHP/extension versions, the lockfile when used, CI, and production. Platform emulation changes dependency resolution; it does not supply a runtime or extensions.
- A reusable package's minimum runtime is a consumer contract. Do not narrow its constraint just because a developer machine runs a newer PHP. Separate compatibility maintenance from deployment of an application.
- Gate enums, readonly classes/properties, typed constants, hooks, and newer syntax on the supported runtime and framework. Prefer the smallest transformation that satisfies the requested goal; features are not a checklist to impose on every project.
- Changing loose `switch` comparisons to strict `match`, adding scalar types, or introducing `strict_types` can change behavior. Trace inputs and callers and use discriminating tests before calling the change equivalent.
- Check constructor promotion against validation, initialization order, inheritance, reflection, and framework hydration. Do not remove meaningful generic or array-shape PHPDoc when native types cannot express it.
- Named arguments, serialized properties, enum backing values, and exception types can be public contracts even when no interface file changes. Account for the project's actual consumers and stored data.

## Framework and object boundaries

- Identify Doctrine ORM version and lazy-loading configuration before judging entity `readonly`, `final`, hooks, or proxies. Native lazy objects support cases that subclass-based proxies cannot; a blanket ban and a blanket conversion are both inappropriate.
- Keep DTO/value-object choices separate from persistence models and API resources unless the project explicitly combines them. Retain legitimate mutation, framework extension points, and mock targets.
- Do not forbid custom `EntityRepository` inheritance or require a particular repository pattern globally. Check the installed ORM/framework contract and local working registrations.
- For Symfony, Laravel, TYPO3, or another framework, inspect actual supported conventions and versions. Do not introduce a framework-specific directory, service container, or coding standard into an unrelated project.
- For PHPUnit/Pest changes, verify the installed version's mock/stub behavior and the assertion's purpose. Never mass-replace mocks with stubs or add `final` indiscriminately.

## Analysis and baseline policy

- Preserve the configured PHPStan/Psalm level unless raising it is part of the task. Inspect finding deltas, baseline scope, extensions, and included config; a file or dependency name alone does not prove effective configuration.
- Use PHPat or another architecture-test tool only if present or explicitly being adopted. A package declaration is not an executed boundary test.
- When dependencies or analysis configuration change, determine cache invalidation from that tool's documented behavior. Do not broadly delete shared temporary directories. A cached report is evidence of its recorded inputs and time, not automatically of the current source.
- Compare baseline entries to actual findings. Remove resolved suppressions deliberately; do not replace the baseline with all current failures or require a commit as part of local verification.

## Tool execution and side effects

- Inspect executable paths, Composer scripts/plugins, test bootstrap, and executable config before running project tools. Running PHPStan, Rector, tests, or a formatter can execute code from the project.
- Resolve the real command for the host and installed version, including Windows launchers when applicable. Do not assume a Unix shebang or `vendor/bin` path is directly executable everywhere.
- Use verified preview flags for Rector and formatters, and review output before scoped apply. A Composer alias can change flag forwarding. Preview may write caches or reports; state and bound those effects.
- Dependency installs/updates can download code, invoke plugins, execute scripts, and change locks/vendor files. Do not perform them as discovery; follow repository policy and the user's authorized implementation scope.
- `composer audit` can contact external services. Mutation tools execute tests and consume substantial resources; profiling and benchmarks measure different claims from static analysis. Run only requested or necessary authorized checks.
- Distinguish planned, executed, passed, failed, skipped, unavailable, and timed-out checks. Do not infer success from an orchestrator exit code if required checks were missing or filtered out.

Primary references: [PHP migration guides](https://www.php.net/manual/en/appendices.php), [Composer platform configuration](https://getcomposer.org/doc/06-config.md#platform), [Doctrine entity restrictions](https://www.doctrine-project.org/projects/doctrine-orm/en/current/reference/architecture.html#entities), [Rector dry run](https://getrector.com/documentation/dry-run).
