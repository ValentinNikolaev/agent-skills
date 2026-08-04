---
name: create-memory
description: Bootstrap durable project memory from a repository and its available instructions. Use when a project has no useful memory index, when memory needs initial creation, or when the user asks to document project context for future agents. Preview broad or destructive writes and keep the result platform-neutral.
metadata:
  trigger: Creating initial project memory
user-invocable: true
allowed-tools: Read, Grep, Glob, Write, Edit, MultiEdit
argument-hint: "[project-root] [memory-root]"
---

# Create Memory

Bootstrap durable memory for a project. This skill belongs to the memory family:

- `create-memory` establishes a useful baseline.
- `ingest-memory` imports external or supplied knowledge.
- `update-memory` records new knowledge from later work.
- `audit-memory` checks quality, links, freshness, and drift.

Keep these as separate workflows. They share the same file conventions and safety rules.

## Scope Discovery

1. Resolve the project root and memory root from the user's arguments first.
2. If no memory root is supplied, inspect likely locations without assuming one platform:
   - a repository-local `memory/` or `memories/`
   - `.claude/memory/`
   - `.codex/memory/`
   - a platform project-memory directory such as Claude's project memory location
   - a global memory directory such as `~/.claude/memory/`
3. Prefer the narrowest root that clearly belongs to the requested project. Do not write to a global root when a project-local root is intended.
4. Read any existing `MEMORY.md` index and memory files before proposing changes.

If several roots are plausible, report the candidates and ask the user to choose before writing. Never silently merge unrelated memory stores.

## What to Inspect

Build a concise project model from available, relevant sources:

- `CLAUDE.md`, `AGENTS.md`, `CODEX.md`, `.claude/`, `.codex/`, and repository instruction files
- README files and architecture or contribution documentation
- package, build, test, deployment, and dependency manifests
- important top-level directories and entry points
- migrations, schemas, configuration, and integration boundaries when present
- recent git history and the current branch state when repository inspection is available
- existing project, feedback, and reference memory
- shallow sibling or global memory only when it is explicitly relevant

Do not scan generated artifacts, dependencies, credentials, secrets, or large data directories unless the user asks for them.

## Candidate Selection

Separate durable knowledge into these family types:

- `project`: architecture, workflows, boundaries, conventions, integrations, and decisions
- `feedback`: recurring user preferences, corrections, or explicit working agreements
- `reference`: stable external facts or technical references needed by future work

Capture knowledge that is stable, non-obvious, and useful in a later session. Skip facts that are already enforced by source code or instructions, temporary task state, secrets, raw logs, and details that can be derived cheaply from the repository.

Before writing, produce a compact candidate plan containing the selected memory root, proposed files, their types, and the evidence for each. Ask for confirmation when the target root was inferred rather than supplied, when the plan would create more than three files, replace an existing index, or modify existing memory in a non-additive way. Small additive bootstraps may proceed after the user has clearly requested creation and the root is unambiguous.

## Family File Standard

Every memory file should use frontmatter like this, adapting fields only when the host memory system requires it:

```yaml
---
name: short-kebab-case-name
description: One sentence describing when this memory is useful.
type: project
related: []
last_updated: YYYY-MM-DD
---
```

Use `type: project`, `feedback`, or `reference`. Preserve an existing `source` field when present and add it when the evidence came from a URL, document, issue, or other external source. Keep `related` entries as stable filenames or identifiers, and maintain links in both directions when practical.

## Write Workflow

1. Read the current index and files one more time before editing.
2. Create the smallest useful set of focused files. Prefer one topic per file over a large narrative.
3. Write evidence-based summaries with decisions, constraints, and verification hints. Do not invent missing context.
4. Create or update `MEMORY.md` as a short navigation index. Include each active memory file, its type, and its purpose.
5. Preserve manual index entries and unrelated files. Do not delete stale material unless the user explicitly requests cleanup.
6. Check that every indexed file exists and every related link resolves within the selected memory root.

Before the final report, run a duplicate pass: compare each new filename, `name`, description, and distinctive claim against existing memory files and the updated `MEMORY.md`. Merge or report duplicates instead of leaving two canonical homes for the same durable fact.

## Safety and Handoff

- Do not write credentials, tokens, private personal data, or raw conversation dumps.
- Do not overwrite an existing memory file merely because a new summary has the same topic. Compare first and propose a merge when information may be lost.
- Keep temporary discoveries out of durable memory unless they meet the candidate criteria.
- Report the selected roots, created or changed files, skipped candidates, and unresolved uncertainties.
- Recommend running `audit-memory` after creation, especially when importing an unfamiliar project or creating more than one file.
