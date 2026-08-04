---
name: clean-code-comments
description: Remove excessive, redundant, or LLM-generated comments from source code in user-specified directories. Use when asked to clean up comments, reduce comment noise, shorten verbose documentation, or remove comments that merely restate self-explanatory code. Preserve intent, constraints, business rules, tooling directives, and non-obvious behavior. Do not use for general refactoring or documentation generation.
metadata:
  trigger: Cleaning redundant source-code comments
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(git status:*), Bash(git diff:*), Bash(rg:*), Bash(find:*), Write, Edit, MultiEdit
argument-hint: "<target directory...> [--dry-audit]"
---

# Clean Code Comments

Clean up comments in source files located within directories explicitly provided by the user.

Reduce comment noise without changing program behavior or performing unrelated refactoring.

## Required input

The user must provide one or more target directories.

If no directories are provided, ask for them before editing files.

Resolve relative paths from the repository root unless the user specifies another base directory.

Only modify files inside the resolved target directories.

If the user passes `--dry-audit`, inspect and report comment-cleanup opportunities without editing files.

## Before editing

1. Verify that every target directory exists.
2. Read applicable repository instructions, including files such as:

   * `AGENTS.md`
   * `CLAUDE.md`
   * `CONTRIBUTING.md`
   * language-specific style guides
3. Identify:

   * source languages;
   * documentation conventions;
   * configured linters and formatters;
   * generated-file markers;
   * comments interpreted by tools.
4. Exclude generated, vendored, minified, cached, compiled, and third-party files unless the user explicitly includes them.

## Comment policy

Read [references/comment-policy.md](references/comment-policy.md) before modifying files.

Use its rules to classify each comment as one of:

* preserve;
* remove;
* shorten;
* rewrite for clarity without changing meaning.

When classification is unclear, consult [references/examples.md](references/examples.md).

## Core rule

For each comment, ask:

> Does this comment communicate useful information that cannot be understood quickly from the code itself?

* If no, remove it.
* If yes but it is verbose, shorten it.
* If it explains intent, constraints, or non-obvious behavior, preserve it.
* If it may be consumed by tooling, preserve it unless its semantics are fully understood.
* When uncertain, preserve potentially important context.

## Editing constraints

This is comment cleanup, not general refactoring.

Do not:

* change program behavior;
* rename symbols merely to eliminate comments;
* redesign functions, methods, types, or modules;
* modify public APIs;
* update dependencies;
* change tests except for formatting directly caused by comment cleanup;
* introduce replacement comments when the code is already clear;
* add comments describing the cleanup itself;
* apply broad formatting changes;
* edit files outside the requested directories.

Allowed changes are limited to:

* removing redundant comments;
* shortening useful but verbose comments;
* clarifying useful comments without changing their meaning;
* removing obsolete commented-out code when clearly safe;
* adjusting whitespace directly affected by comment removal;
* running the repository formatter on touched files when appropriate.

## Workflow

### 1. Discover files

Find source files within the target directories.

Respect repository ignore rules where appropriate.

Common exclusions include:

```text
.git
vendor
node_modules
dist
build
target
coverage
.next
.cache
__pycache__
```

Do not rely only on directory names. Also inspect file headers and repository conventions for generated or externally managed files.

### 2. Inspect comments in context

Review enough surrounding code to understand:

* whether the comment only narrates the implementation;
* whether it explains why the implementation exists;
* whether it documents business or domain behavior;
* whether it records an external compatibility requirement;
* whether a tool parses it;
* whether the code would remain clear after removal.

Do not classify comments from their text alone.

### 3. Apply focused changes

Prefer:

1. removal when no comment is needed;
2. shortening when useful context is mixed with narration;
3. rewriting only when the comment is useful but unclear;
4. preservation when purpose or tooling impact is uncertain.

Keep the original language and terminology of retained comments unless clarity requires a small correction.

### 4. Review the diff

Inspect the complete diff before validation.

Confirm that:

* all changed files are inside the requested directories;
* changes are limited to comments and directly affected whitespace;
* no directives or annotations were removed accidentally;
* no business, security, compatibility, or operational context was lost;
* no code behavior changed;
* no unrelated formatter churn was introduced.

Revert unrelated changes.

### 5. Validate

Run the narrowest relevant validation available for the modified files, such as:

* formatter checks;
* compilation;
* static analysis;
* linting;
* targeted tests;
* documentation generation checks.

Do not make unrelated code changes to fix pre-existing failures.

If validation cannot be run or fails for unrelated reasons, report that clearly.

## Completion report

Return a concise report containing:

* processed directories;
* number of files inspected;
* number of files changed;
* main categories of comments removed or shortened;
* validation commands executed;
* validation results;
* skipped files or directories and the reason;
* ambiguous comments intentionally preserved.

Do not enumerate every comment change unless the user explicitly requests a detailed audit.

## Success criteria

The task is complete when:

* redundant comment noise is reduced;
* useful context remains intact;
* tooling-sensitive comments remain intact;
* behavior and public APIs are unchanged;
* the diff contains no unrelated refactoring;
* relevant validation has been run or its absence has been explained.
