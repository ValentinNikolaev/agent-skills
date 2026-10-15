# TypeScript Review Checks

Apply only to changed TypeScript behavior, declarations, module/build configuration, and nearby tests. Include `.ts`, `.tsx`, `.mts`, and `.cts` as applicable. Read the owning `package.json`, dependency/lock boundary, effective `tsconfig` chain or project references, build/test commands, compiler version, and supported runtimes. Do not assume Node.js, a browser, Bun, Deno, Next.js, React, Jest, Vitest, or a particular module system.

## Types and runtime contracts

- Trace values from runtime input to use. Static types do not validate JSON, form data, environment values, or third-party responses; check validation at the actual trust boundary.
- Review nullability and indexed access against the project's compiler options. A cast, non-null assertion, or `any` may hide a real missing case; demonstrate the reachable value before flagging it.
- For discriminated unions, inspect every branch after a variant or field changes. An exhaustive `never` check can expose missing variants, but do not demand one when the repository uses another sound pattern.
- Check optional fields and explicit `undefined` against compiler settings and runtime operations such as property-presence checks, object spread, updates, and serialization. An absent field and a present field with value `undefined` need not mean the same thing.
- Treat `as`, non-null assertions, `satisfies`, user-defined type guards, and generic constraints according to what they actually establish. An assertion or a generic return type does not validate external data. Check that a predicate's implementation proves the shape it claims.
- Trace reference sharing through shallow copies, `readonly` types, arrays, maps, caches, and callbacks. Type-level readonly is not a runtime freeze or deep immutability guarantee. Report a mutation only when it breaks a concrete consumer contract.
- When public types or exports change, search consumers and runtime serializers as well as the compiler-visible call sites. Type compatibility does not establish wire-format compatibility.
- For public generic/function/interface changes, inspect representative consumers, overload selection, structural compatibility, and emitted declarations. A local compile does not establish compatibility with downstream compilers or declaration consumers.
- Check number/string/date conversions, truthiness, missing indexed values, and method receiver binding on reachable inputs. Do not flag a style preference or every use of `any` as a defect.

## Async work, failure, and ownership

- Follow promises across callers, handlers, and cleanup. Check omitted `await`, rejected promises, and errors transformed into success where the changed path makes them relevant. An async callback passed to `forEach` or an event API does not mean that API awaits it.
- Check whether `Promise.all`, `allSettled`, sequential work, or detached tasks match the required ordering, failure handling, and resource bounds. A rejection does not automatically cancel other operations or roll back their side effects.
- Trace cancellation from its owner to the actual operation. An `AbortSignal` parameter or a timeout race is not proof that underlying work stops. Check stale results and cleanup after cancellation, component disposal, or caller return.
- Check closure-captured state, event listeners, subscriptions, timers, streams, and sync/async disposal on normal and exceptional exits. Give each resource a lifetime owner; do not require new resource-management syntax without runtime support.
- For many inputs, distinguish active concurrency from queued promises and retained data. Do not introduce pooling, caching, or parallelism as a speculative optimization.

## Modules and execution

- When module configuration changes, reconcile `package.json` type/exports, file extensions, compiler module resolution, emitted files, and the deployed loader. `tsconfig` paths do not rewrite emitted imports or guarantee runtime aliases work.
- For published packages, inspect import/require/types conditions, subpaths, wildcard exports, and consumers using supported loaders. A wildcard can expose an internal path; separate declaration-file success from loading the emitted JavaScript.
- Distinguish type-only imports/exports from runtime dependencies and side-effect imports. Check the actual transpiler's handling of enums, decorators, class fields, and other emitted constructs instead of assuming every runner behaves like `tsc`.
- For decorators and explicit resource management, verify compiler options, framework expectations, runtime support, and sync/async cleanup on normal and exceptional exits. Do not recommend new syntax solely because the compiler accepts it.
- For monorepos and project references, identify the owning package/config and whether tests consume source or built output. Hoisted dependencies and workspace aliases can mask missing published dependencies or broken emitted imports.

## Conditional framework and security checks

- In UI or server frameworks, trace the actual client/server boundary, permission check, and side effect. Apply framework-specific rules only after identifying the installed version and local pattern. Check closure freshness, effects, teardown, and hydration only where that framework and changed behavior make them relevant.
- For client caches, inspect keys and invalidation across tenant/user changes, mutations, and stale requests. Demonstrate a reachable data leak or stale result using the installed framework's semantics before reporting it; do not require a particular query library.
- Check authorization and validation at the server boundary even when shared TypeScript types or client-side schemas exist. Trace untrusted values into HTML, SQL, shell arguments, URLs, dynamic property writes, and logs using the shared security checklist only when relevant.

## Tests

- Use the repository's runner and test environment. Do not translate Jest examples into Vitest or vice versa without checking configuration and semantics.
- Check that async work is awaited and that assertions distinguish success from a vacuous pass or a swallowed rejection.
- Mock external boundaries while keeping the changed business behavior observable. Verify reset or isolation when mocks or module state are shared across tests.
- Check fake timers, pending microtasks, rejected promises, and teardown with the actual runner's semantics. Advancing a timer does not universally flush all async work, and an unreturned promise can let a test finish before its assertion.
- For component tests, check user-visible behavior and accessible roles when the component's interaction changes; use the project's existing tools and query conventions. Do not demand UI tests for non-UI code.
- Keep type-level tests distinct from runtime tests. A transpile-only loader, Node type stripping, or a test runner may execute `.ts` while performing no type check; a successful type check still cannot prove runtime input validation.
- When a new variant, validation rule, or failure path is added, identify the exact missing test scenario and whether an existing test already covers it.

## Verification

Use documented targeted type-check and test commands when they materially verify a finding. A green type check cannot prove runtime validation or UI behavior. Treat a skipped test and a test filter that matched nothing as unrun, not a pass.

Record the exact project/package selection and configured tool versions. Do not assume that passing filenames directly to a compiler uses the same configuration as the repository's project command. Do not install TypeScript, replace the package manager, run formatter fixes, change strictness flags, or regenerate locks merely to conduct review. Note cache/build-output writes when relevant.

TypeScript references: [narrowing and exhaustiveness](https://www.typescriptlang.org/docs/handbook/2/narrowing.html), [`noUncheckedIndexedAccess`](https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html).

Selected type-safety, async, module, resource-management, and testing topics adapt awesome-skills/code-review-skill, `reference/typescript.md`, at commit `4850184dfd7765ea7b3c5c4e9b6cf8e0815ee7cb`; see `LICENSE.awesome-skills`. Primary references: [TypeScript module resolution](https://www.typescriptlang.org/docs/handbook/modules/reference.html), [exact optional properties](https://www.typescriptlang.org/tsconfig/exactOptionalPropertyTypes.html), [Node.js package exports](https://nodejs.org/api/packages.html#subpath-patterns), [Node.js type stripping](https://nodejs.org/api/typescript.html).
