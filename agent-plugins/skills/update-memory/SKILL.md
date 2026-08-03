---
name: update-memory
description: Maintain existing agent memory after a work session, feature, fix, decision, or project milestone. Use when durable knowledge changed and the user asks to update, record, sync, or maintain project memory. Avoid speculative or temporary notes and preview ambiguous edits.
metadata:
  trigger: Updating existing project memory
user-invocable: true
allowed-tools: Read, Grep, Glob, Write, Edit, MultiEdit
argument-hint: "[session-scope] [project-root] [memory-root]"
---

# Update Memory

Maintain existing durable memory after project work. This is the maintenance member of the memory family:

- `create-memory` bootstraps the initial baseline
- `ingest-memory` imports source material
- `update-memory` records changes learned during work
- `audit-memory` validates the resulting memory set

Keep the skills separate while applying the same file, link, and safety conventions.

## Establish Context

1. Resolve the project and memory roots from the user's arguments or current repository context.
2. Locate the active `MEMORY.md` index and read the relevant memory files before editing.
3. Gather available session evidence: the user's summary, decisions made, completed work, important failures, changed interfaces, tests, and follow-up constraints.
4. When repository inspection is available, use focused `git diff`, `git log`, branch information, and changed files as supporting evidence. Treat git history as evidence, not as a substitute for user intent.
5. Consider repository-local `memory/`, `.claude/memory/`, `.codex/memory/`, platform project memory, and global memory according to the selected scope. Do not silently update multiple roots.

If the scope or target root is ambiguous, report the candidates and ask before writing.

## Decide Whether to Write

Write memory when the session produced a durable:

- architectural or product decision
- workflow or integration constraint
- recurring user preference or correction
- resolved failure whose cause and prevention matter later
- shipped behavior, migration, contract, or operational milestone
- source-backed fact that future work will need

Do not write for:

- temporary task progress or an unfinished experiment
- information already obvious from code or existing instructions
- routine implementation details with no future decision value
- secrets, tokens, private data, raw logs, or full conversation transcripts
- speculative ideas that were not adopted

Use this decision order:

1. If an existing memory file directly covers the topic, update it only when the durable truth changed.
2. If the topic is durable but absent, propose a focused new file.
3. If it is temporary, redundant, or uncertain, skip it and report why.

Preview the proposed file-level changes and ask for confirmation when edits are ambiguous, overwrite substantial existing text, create more than three files, or change relationships across multiple topics. Small, clearly requested updates may proceed additively.

## Family File Standard

Use or preserve this frontmatter shape:

```yaml
---
name: short-kebab-case-name
description: One sentence describing when this memory is useful.
type: project
related: []
last_updated: YYYY-MM-DD
---
```

Allowed types are `project`, `feedback`, and `reference`. Preserve an existing `source` field and its provenance. Preserve manual `related` entries, add reciprocal links when useful, and update `last_updated` only when the durable content changes.

## Update Workflow

1. Summarize the new durable fact in one sentence before editing.
2. Compare it with the existing memory to avoid duplicate or contradictory statements.
3. Update the smallest focused section or create one focused file. Retain useful historical context when it explains why the current state exists.
4. Mark unresolved conflicts or superseded decisions explicitly instead of deleting context without explanation.
5. Update `MEMORY.md` only when files or their purposes changed. Keep the index short and navigational.
6. Verify every index entry and related link resolves within the selected memory root.

## Report and Handoff

Report the evidence used, files changed, facts skipped, conflicts, and any follow-up needed. Recommend `audit-memory` after cross-file edits or when the update changes the index, links, or source provenance.

