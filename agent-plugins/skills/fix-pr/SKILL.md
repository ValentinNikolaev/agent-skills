---
name: fix-pr
description: Triage and fix actionable GitHub pull-request review feedback. Use when the user asks to address PR comments, fix review feedback, apply suggestions, or resolve requested changes. Preserve non-actionable comments in the report, make minimal edits, verify the result, and never commit or push unless explicitly asked.
metadata:
  trigger: Fixing GitHub pull request review feedback
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(git status:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(git fetch:*), Bash(git checkout:*), Bash(git worktree:*), Bash(git diff:*), Bash(git log:*), Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh api:*), Bash(rg:*), Write, Edit, MultiEdit
argument-hint: "<PR URL or owner/repo#number>"
effort: thorough
---

# Fix Pull Request Review Feedback

Inspect a GitHub pull request, separate actionable feedback from comments that need no code change, apply the smallest correct fixes, and verify the result. This skill changes files and may change the checked-out branch, so protect local work throughout the workflow.

## Safety and Preconditions

1. Confirm the PR reference and repository before changing anything.
2. Inspect the current branch and working tree. If there are uncommitted changes, do not stash, reset, clean, or overwrite them. Ask the user whether to continue, use a separate worktree, or stop.
3. Confirm that the GitHub connector or CLI is authenticated before attempting to fetch review data.
4. Record the starting branch and commit so the final report can describe any branch change.
5. Do not commit, push, resolve GitHub threads, or send external comments unless the user explicitly requests that follow-up.
6. Ask before changing branches or creating a worktree unless the user already requested working on that PR branch in this turn.

## Parse the PR Reference

Accept:

- a full URL such as `https://github.com/owner/repo/pull/123`
- a URL with a suffix such as `/files`, `/commits`, or `/checks`
- shorthand such as `owner/repo#123`

Extract owner, repository, and number. Strip query parameters and trailing PR subpaths. If parsing fails, report the accepted formats and stop.

## Prepare the Local Repository

If the requested PR is not represented by the current branch, use the available GitHub or git capability to inspect or check out the PR branch. Do not discard local work. If checkout would overwrite changes, stop and report the exact precondition.

Prefer a separate worktree when the current repository is clean but the user needs to preserve their current branch. Otherwise, record the branch transition and return to the starting branch only when that can be done without affecting unrelated work.

## Fetch Review Data

Use a GitHub connector or CLI/API capability. GraphQL is preferred for inline review threads because it exposes resolution and outdated status; use an equivalent API when it provides the same information. If only flat review comments are available, label thread resolution and outdated status as unknown rather than guessing.

Collect:

- PR title and author
- inline review threads with path, line range, resolution, outdated status, authors, and comments
- general issue-level PR comments
- pagination until all relevant comments are collected

Never treat a bot summary as a human change request. Keep author identity and timestamps for the final report.

## Classify Feedback

Process the first applicable rule in this order:

1. Resolved thread: skip as `resolved`.
2. Thread containing only the PR author's comments: skip as `author comment`.
3. Generated bot summary without a direct request: skip as `bot summary`.
4. A GitHub `suggestion` block: actionable.
5. Praise without a requested change: skip as `praise`.
6. A question without a direct change request: skip as `question - needs human response`.
7. A concrete request to change code, tests, configuration, or documentation: actionable.
8. An outdated thread whose referenced file and code pattern still exist: actionable after locating the current position.
9. An outdated thread whose file or code no longer exists: skip as `outdated - no current target`.
10. Anything ambiguous: skip as `ambiguous - needs human review`.

For general comments, use the same request, praise, question, bot, and ambiguity rules. If a general request has no clear file or code target, report it for human clarification instead of guessing.

For multi-comment threads, use the last reviewer comment that is not by the PR author as the current request, while retaining earlier comments as context.

## Report Before Editing

Before changing files, report all non-actionable comments in a compact table containing:

- number
- file and line, or `(general)`
- reviewer
- reason
- short summary

Then list the actionable items and their intended files. If an actionable item is ambiguous or would require a broad refactor, pause for clarification.

## Apply Minimal Fixes

Group work by file and preserve project conventions.

For suggestion blocks:

1. Read the target file and exact line range.
2. Confirm the suggested range still matches the current content.
3. Apply only the replacement text from the suggestion.
4. If the range no longer matches, locate the original code pattern and report uncertainty before editing.

For prose requests:

1. Read the target file and surrounding context.
2. Read applicable project instructions and path-scoped rules.
3. Implement the smallest change that satisfies the reviewer.
4. Add or adjust tests when the feedback changes behavior or exposes a missing case.

For outdated but applicable threads, search for the referenced symbol or code pattern and apply the fix only after confirming the new location.

Do not silently expand a review comment into unrelated cleanup, style changes, or speculative improvements.

## Generated and Renamed Files

- Do not edit generated files directly. Identify the generator and report the regeneration command.
- If a target file was renamed, inspect read-only history to locate the new path before applying a fix.
- If the target was deleted, report the item as unresolved unless the reviewer request clearly applies elsewhere.

## Verify

Inspect available project instructions, manifests, and build configuration to select applicable checks. Run non-destructive checks in a sensible order:

1. regenerate derived artifacts only when the changed source requires it
2. format changed files when the project defines a formatter
3. lint or static analysis
4. compile or build
5. focused unit tests
6. broader or integration tests when relevant and available

Use the repository's documented commands first. If no commands are documented, choose the language's standard checks from its manifests. Distinguish failures caused by the edits from pre-existing or environment failures.

Review the final diff and confirm that only intended files changed. Do not stage or commit unless explicitly requested.

## Final Report

Return:

- PR identity and title
- fixes applied, with file and line context where available
- non-actionable comments and reasons
- warnings for unresolved, outdated, generated, or ambiguous items
- verification commands and results
- current branch and working-tree state
- next steps requiring human response
