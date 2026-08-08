# Comment Cleanup Policy

Use this normative policy before classifying comments in edit or dry-audit mode.

## Contents

- [Decision rule](#decision-rule)
- [Remove narration](#remove-narration)
- [Preserve non-obvious context](#preserve-non-obvious-context)
- [Shorten or rewrite](#shorten-or-rewrite)
- [Documentation comments](#documentation-comments)
- [Tool-interpreted comments](#tool-interpreted-comments)
- [TODO-style markers](#todo-style-markers)
- [Commented-out code](#commented-out-code)
- [Ambiguity](#ambiguity)

## Decision rule

Read the comment with its code, repository rules, and relevant configuration. Ask whether it communicates useful information that a maintainer cannot recover quickly from the implementation.

- If no, classify `remove`.
- If yes but verbose, classify `shorten`.
- If useful but inaccurate or unclear, classify `rewrite` only when the correct meaning is already evidenced nearby.
- If it explains intent, a constraint, or non-obvious behavior accurately, classify `preserve`.
- If it is externally managed or outside authorized scope, classify `skip`.
- If meaning or tooling impact cannot be established, classify `question` and preserve it.

Never invent facts, owners, issue IDs, deadlines, behavior, or rationale to justify retaining a comment.

## Remove narration

Remove comments that only translate adjacent code into natural language. Common cases:

- repeating a symbol, type, signature, or literal value;
- describing the next statement or standard syntax;
- narrating obvious control flow, validation, iteration, assignment, or return;
- labeling a short self-explanatory block;
- repeating information enforced by types;
- generic declaration documentation added mechanically;
- decorative headings that do not improve navigation.

Do not use perceived “AI style” as evidence. Judge the information value.

## Preserve non-obvious context

Preserve accurate comments that explain:

- business or domain rules;
- external-system behavior;
- security or privacy constraints;
- concurrency, ownership, ordering, retry, timeout, or idempotency requirements;
- performance-sensitive decisions or resource bounds;
- compatibility, migration, or platform limitations;
- deliberate deviations from repository conventions;
- non-obvious invariants, side effects, or data semantics;
- why a simpler-looking implementation is unsafe.

Verify factual claims when practical. An obsolete rationale is not useful merely because it once explained “why.”

## Shorten or rewrite

Shorten when useful rationale is mixed with history, repetition, filler, or line-by-line narration. Preserve the operative constraint and important qualifiers.

Rewrite only when:

- the comment remains necessary;
- current code or authoritative local documentation proves the intended meaning;
- the edit does not strengthen, weaken, or broaden the contract.

Remove rather than replace when code is already clear.

## Documentation comments

Treat public API documentation separately from ordinary inline comments.

Preserve documentation required by repository conventions, language ecosystems, configured linters, documentation generators, or public API policy. Improve it only when the implementation proves the correction.

For private symbols, remove documentation that adds no context. For required public documentation that is redundant but cannot safely be improved, preserve and report it rather than breaking the documentation contract.

## Tool-interpreted comments

Never remove or alter a comment that may affect compilation, generation, formatting, linting, type checking, testing, coverage, documentation, dependency injection, ORM behavior, or runtime metadata unless its exact semantics and removal safety are proven.

Protected categories include:

- build tags, compiler pragmas, and shell directives;
- formatter, lint, type-checker, test, and coverage directives;
- code-generation instructions and generated-file markers;
- OpenAPI, Swagger, ORM, framework, and structured docblock annotations;
- license, copyright, and required attribution headers;
- editor directives when repository policy retains them.

Search configuration and nearby usage for unfamiliar structured comments. Preserve first when uncertain.

## TODO-style markers

Markers include `TODO`, `FIXME`, `HACK`, `NOTE`, and `WORKAROUND`.

- Preserve a marker with a concrete constraint, migration condition, failure, or actionable next step.
- Remove a marker that is clearly content-free and has no repository-specific value.
- Shorten or clarify only from evidence already present nearby.
- Do not fabricate an owner, ticket, deadline, cause, or solution.

## Commented-out code

Remove commented-out code only when it is clearly obsolete, version control preserves its history, and it is not part of a fixture, sample, template, tutorial, or compatibility case.

Preserve when repository conventions require it or a concrete explanation shows why it must remain temporarily. Do not uncomment, repair, or restore it during comment cleanup.

## Ambiguity

Preserve and report a materially ambiguous comment when:

- its tooling role is unknown;
- its domain meaning cannot be established;
- removal may hide a requirement or operational constraint;
- authoritative rules conflict;
- the file is externally managed or outside authorized scope.

Do not list every minor preserved comment. Report ambiguity when it affects cleanup coverage or future maintenance.
