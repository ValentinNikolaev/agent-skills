# PHP Review Checks

Apply only to changed PHP behavior, PHP-backed templates, and nearby tests. Read `composer.json`, the relevant lockfile when present, supported PHP versions and extensions, CI, analysis configuration, and the installed framework/ORM versions. Distinguish a deployed application from a reusable library; do not assume Laravel, Symfony, Doctrine, PHPStan, or Psalm.

Selected topics are adapted from awesome-skills/code-review-skill at commit `4850184dfd7765ea7b3c5c4e9b6cf8e0815ee7cb`, `reference/php.md`; see `LICENSE.awesome-skills` in this package. This reference does not adopt a company's formatting or architecture conventions.

## Values and public contracts

- Trace loose comparisons, numeric strings, truthiness, `isset`, `empty`, missing keys, and nulls using reachable inputs. Check authorization, token comparison, identifiers, and money paths before calling type juggling a defect. Use appropriate constant-time comparison for secrets when required by the contract.
- Check parameter, return, property, union, and enum changes against callers, serializers, persistence, and the minimum runtime. Named-argument callers can depend on parameter names. New types or `strict_types` can change behavior; do not prescribe them as a cosmetic fix.
- Inspect the caller file's strict-typing mode at relevant scalar calls. A declaration in the callee file does not make all external callers strict.
- Check uninitialized typed properties, dynamic properties, nullsafe chains, and defaults against construction and hydration paths. Nullsafe access must not conceal a required missing state.
- Distinguish immutable DTOs/value objects from entities, proxies, framework extension points, and mocks. Check the actual ORM version and lazy-loading mode before judging `readonly`, `final`, property hooks, or constructor promotion. Do not ban or require them globally.
- Check PHPDoc generics, array shapes, and conditional types for information absent from native declarations. Do not remove meaningful annotations merely because native types exist.

## Trust boundaries and data

- Follow request, CLI, environment, uploaded-file, queue, and external API data through validation and coercion to use. Type declarations alone do not establish a validated domain value.
- Check SQL parameter binding and dynamic identifiers separately. ORM use does not make raw expressions safe. Trace tenant ownership and authorization on the server, not just a hidden template action.
- Match output encoding to HTML, attributes, URLs, JavaScript, and other actual contexts. Check raw-template escapes and stored content. Input validation does not replace output encoding.
- Check password APIs, randomness, secret comparisons, untrusted `unserialize`, shell construction, and executable PHP configuration. Do not execute a PHP config file just to inspect an untrusted repository.
- For uploads and file operations, trace MIME/size restrictions, traversal, resolved paths, symlinks, storage permissions, and whether uploaded content can execute.
- Trace transaction boundaries and side effects in order. External requests or queue publication do not roll back with a database transaction; check idempotency, retry behavior, and partial failures.
- Check lazy ORM access, N+1 queries, hydration cost, cursor lifetime, and large collections only on affected paths. Preserve version-specific repository and mapping conventions when sound.

## Errors, resources, and dependencies

- Distinguish `Exception`, `Error`, and `Throwable` where the changed path needs that coverage. Inspect suppressed errors, false/null return values, exception translation, and cleanup instead of prescribing blanket catches.
- Check stream, file, connection, and worker lifetimes and sensitive log content. Long-running processes can retain static state, caches, or ORM-managed objects across jobs.
- Compare Composer platform constraints, extensions, resolved packages, autoloading, and production dependency boundaries. An application lockfile and a library's dependency policy have different roles; do not require a lockfile in every library.
- Check changed baselines and ignore rules against actual findings. A PHPStan level or installed PHPat package does not prove the affected code or architecture tests ran. Do not raise levels, regenerate baselines, install tools, or update dependencies during review.

## Tests and verification

- Use configured PHPUnit, Pest, or other tests. Check the observable behavior, error paths, fixture isolation, clocks, queues, database state, and mocks/stubs against the installed test framework version.
- For ORM changes, inspect appropriate persistence/hydration and lazy-loading tests; a DTO unit test does not establish entity compatibility. For public packages, verify the supported runtime and consumer matrix proportionately.
- Prefer documented narrow test and analysis commands. Distinguish syntax checks, class loading, static analysis, and behavior tests: none substitutes for all the others.
- Do not run formatter fixes or Rector apply during read-only review. Preview/tool runs can still execute project configuration or write caches; inspect their behavior and respect the main skill's cost and side-effect boundaries.
- Report `not run`, `skipped`, missing tools, and unsupported runtime cells explicitly. Never equate exit code zero with complete verification.

Primary references: [PHP type declarations](https://www.php.net/manual/en/language.types.declarations.php), [Composer libraries and lockfiles](https://getcomposer.org/doc/02-libraries.md#lock-file), [Doctrine entity restrictions](https://www.doctrine-project.org/projects/doctrine-orm/en/current/reference/architecture.html#entities).
