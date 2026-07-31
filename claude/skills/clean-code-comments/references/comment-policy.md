# Comment Cleanup Policy

Use this reference when reviewing comments during the `clean-code-comments` workflow.

## Remove comments that restate code

Remove a comment when it merely translates the adjacent code into natural language.

Common cases include comments that:

* repeat a function, method, field, variable, type, or constant name;
* describe the next statement literally;
* narrate obvious control flow;
* explain standard language syntax;
* repeat information already represented by types or signatures;
* label a short and obvious block;
* describe routine initialization, validation, iteration, assignment, or return operations;
* contain generic statements without project-specific context;
* appear to exist only because every declaration was mechanically documented.

Examples of weak patterns:

```text
Increment the counter.
Return the result.
Check whether the error is not nil.
Create a new user.
Initialize an empty list.
Loop through all items.
Set the default timeout.
```

Remove decorative section headings such as:

```text
Initialization
Validation
Processing
Handle error
Return result
```

when the section is short and the code already makes its purpose clear.

## Preserve comments that explain why

Preserve comments that communicate information not apparent from the local implementation.

This includes:

* business rules;
* domain semantics;
* external-system behavior;
* compatibility requirements;
* security constraints;
* concurrency assumptions;
* performance-sensitive decisions;
* non-obvious invariants;
* unusual operation ordering;
* retry, timeout, or idempotency behavior;
* required side effects;
* migration constraints;
* backward compatibility;
* known platform, compiler, framework, or library limitations;
* deliberate deviations from normal project patterns;
* workarounds with a concrete reason;
* data semantics not represented by types;
* reasons an apparently simpler implementation is unsafe.

A useful comment should usually explain one of:

* why this code exists;
* why this approach was chosen;
* why an obvious alternative is not used;
* what external constraint must remain true;
* what future maintainer could accidentally break.

## Shorten verbose comments

Shorten a comment when it contains useful information but includes unnecessary narration, history, repetition, or implementation detail.

Prefer one direct statement of the constraint or rationale.

Verbose:

```go
// We need to sort the records by creation time here because the external
// reporting API expects all records to be sent in chronological order,
// otherwise the API can produce incorrect cumulative totals in its reports.
```

Better:

```go
// Reporting totals require records in chronological order.
```

Do not shorten a comment so aggressively that the reason or constraint becomes unclear.

## Documentation comments

Treat public API documentation separately from ordinary inline comments.

Preserve documentation required by:

* repository conventions;
* language ecosystems;
* configured linters;
* documentation generators;
* public API standards.

Required documentation should still add information.

Weak:

```go
// UserService is a user service.
```

Better:

```go
// UserService manages registration and account lifecycle operations.
```

For private symbols, remove documentation that adds no context.

Do not invent behavior merely to make a documentation comment sound useful. When no meaningful description is available and documentation is not mandatory, remove the comment.

## Tool-interpreted comments

Never remove or alter comments that may affect compilation, generation, linting, testing, documentation, or runtime behavior unless their semantics are fully understood.

Examples include:

* build tags;
* compiler directives;
* formatter directives;
* lint suppressions;
* code-generation directives;
* coverage directives;
* test framework directives;
* OpenAPI and Swagger annotations;
* ORM annotations;
* dependency injection annotations;
* framework metadata;
* shell directives;
* editor directives;
* structured docblocks;
* generated-file markers;
* license and copyright headers.

Common examples:

```go
//go:build linux
//go:generate mockgen ...
//nolint:gocyclo
```

```typescript
// eslint-disable-next-line
// @ts-ignore
// @ts-expect-error
```

```php
/** @var User $user */
/** @phpstan-ignore-next-line */
```

```python
# noqa
# type: ignore
```

```c
#pragma once
```

An unfamiliar comment is not automatically redundant. Search nearby configuration or repository usage before modifying it.

## TODO-style markers

Markers include:

* `TODO`
* `FIXME`
* `HACK`
* `NOTE`
* `WORKAROUND`

Preserve them when they contain concrete and useful information.

Useful:

```go
// TODO: Remove this fallback after all clients migrate to API v2.
```

Weak:

```go
// TODO: Fix this.
```

For vague markers:

* remove them when they provide no actionable context and clearly have no current value;
* shorten or clarify them only when the necessary information is already present nearby;
* do not invent owners, issue numbers, deadlines, causes, or intended solutions.

## Commented-out code

Commented-out code is not explanatory documentation.

Remove it when:

* it is clearly obsolete;
* version control already preserves its history;
* no surrounding explanation shows that it is intentionally retained;
* it is not part of a fixture, sample, template, or tutorial.

Preserve it when:

* repository conventions require it;
* it demonstrates an important compatibility case;
* it belongs to a test fixture or documentation example;
* a concrete comment explains why it must remain temporarily.

Do not uncomment, repair, or restore commented-out code as part of this task.

## Ambiguity rule

Preserve a comment when:

* its tooling role is uncertain;
* its domain meaning cannot be established from the available context;
* removing it may hide a requirement or operational constraint;
* repository conventions conflict or are incomplete.

Mention materially ambiguous preserved comments in the completion report without listing every minor case.
