# Version Boundaries

Read the actual installed package and import path first. This is a selective migration checklist, not a replacement for the [official migration guide](https://zod.dev/v4/changelog) or installed declarations.

- Zod 4 requires both key and value schemas for `z.record`; enum-key records also introduce exhaustiveness semantics. Check whether a partial record is intended.
- Error customization, formatting helpers, defaults, and function-validation APIs changed between v3 and v4. Preserve the caller's error/status contract rather than mechanically renaming methods.
- In Zod 4, defaults can appear inside optional object properties. Test the parsed object's actual keys and serialization; TypeScript compatibility alone can miss a wire-format change.
- Number schemas reject non-finite values before refinements. A later `.refine()` cannot re-admit a value already rejected by its base schema. Model a deliberate alternative from the actual accepted domain.
- String format methods and object-composition APIs have version-specific preferred forms. Do not treat a deprecated but functioning method as a correctness defect without a changed contract.
- Codecs require Zod 4.1+. Check the installed minor version for newer APIs and safe/async variants. Mini has a distinct functional surface; core targets library authors and is not a drop-in application API.
- In an upgrade, inventory input acceptance, defaults, transforms, unknown keys, errors, async behavior, and output serialization. Verify representative consumers before claiming compatibility. A downgrade of the package does not by itself restore changed source or stored data.

Official references: [schema APIs](https://zod.dev/api), [codecs](https://zod.dev/codecs), [library-author version/import guidance](https://zod.dev/library-authors).
