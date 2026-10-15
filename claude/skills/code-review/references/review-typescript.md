# TypeScript Review Checks

Apply these checks only to changed TypeScript or TSX behavior and nearby tests. Read `package.json`, lockfile, `tsconfig` files, and the relevant runtime or framework boundary before applying a language rule. Do not assume Next.js, React, Jest, Vitest, or a particular module system.

## Production code

- Trace values from runtime input to use. Static types do not validate JSON, form data, environment values, or third-party responses; check validation at the actual trust boundary.
- Review nullability and indexed access against the project's compiler options. A cast, non-null assertion, or `any` may hide a real missing case; demonstrate the reachable value before flagging it.
- For discriminated unions, inspect every branch after a variant or field changes. An exhaustive `never` check can expose missing variants, but do not demand one when the repository uses another sound pattern.
- Follow promises across callers, handlers, and cleanup. Check omitted `await`, rejected promises, cancellation, stale state, and errors transformed into success where the changed path makes them relevant.
- When public types or exports change, search consumers and runtime serializers as well as the compiler-visible call sites. Type compatibility does not establish wire-format compatibility.
- In UI or server frameworks, trace the actual client/server boundary, permission check, and side effect. Apply framework-specific rules only after identifying the installed version and local pattern.
- When module configuration changes, reconcile `package.json` type/exports, file extensions, compiler module resolution, emitted files, and the deployed loader. `tsconfig` paths do not rewrite emitted imports or guarantee runtime aliases work.
- For published packages, inspect import/require/types conditions, subpaths, wildcard exports, and consumers using supported loaders. A wildcard can expose an internal path; separate declaration-file success from loading the emitted JavaScript.
- For decorators and explicit resource management, verify compiler options, framework expectations, runtime support, and sync/async cleanup on normal and exceptional exits. Do not recommend new syntax solely because the compiler accepts it.
- For client caches, inspect keys and invalidation across tenant/user changes, mutations, and stale requests. Demonstrate a reachable data leak or stale result using the installed framework's semantics before reporting it; do not require a particular query library.

## Tests

- Use the repository's runner and test environment. Do not translate Jest examples into Vitest or vice versa without checking configuration and semantics.
- Check that async work is awaited and that assertions distinguish success from a vacuous pass or a swallowed rejection.
- Mock external boundaries while keeping the changed business behavior observable. Verify reset or isolation when mocks or module state are shared across tests.
- For component tests, check user-visible behavior and accessible roles when the component's interaction changes; use the project's existing tools and query conventions. Do not demand UI tests for non-UI code.
- When a new variant, validation rule, or failure path is added, identify the exact missing test scenario and whether an existing test already covers it.

## Verification

Use documented targeted type-check and test commands when they materially verify a finding. A green type check cannot prove runtime validation or UI behavior. Treat a skipped test and a test filter that matched nothing as unrun, not a pass.

TypeScript references: [narrowing and exhaustiveness](https://www.typescriptlang.org/docs/handbook/2/narrowing.html), [`noUncheckedIndexedAccess`](https://www.typescriptlang.org/tsconfig/noUncheckedIndexedAccess.html).

Module and resource-management topics adapt selected ideas from awesome-skills/code-review-skill, `reference/typescript.md`, at commit `4850184dfd7765ea7b3c5c4e9b6cf8e0815ee7cb`; see `LICENSE.awesome-skills`. Primary references: [TypeScript module resolution](https://www.typescriptlang.org/docs/handbook/modules/reference.html), [Node.js package exports](https://nodejs.org/api/packages.html#subpath-patterns).
