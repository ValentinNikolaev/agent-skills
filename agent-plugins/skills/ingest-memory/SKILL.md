---
name: ingest-memory
description: Import durable knowledge into an agent memory store from a URL, document, provider record, pasted text, project specification, or refreshed source. Use when the user asks to ingest, sync, refresh, or convert external knowledge into structured memory. Detect duplicates and preview risky writes.
metadata:
  trigger: Ingesting external knowledge into memory
user-invocable: true
allowed-tools: Read, Grep, Glob, Write, Edit, MultiEdit
argument-hint: "<source> [--tree] [--prd] [--refresh] [memory-root]"
---

# Ingest Memory

Convert supplied or externally fetched knowledge into durable, navigable memory. This is the import member of the memory family:

- use `create-memory` for repository bootstrap
- use `ingest-memory` for external or supplied source material
- use `update-memory` for knowledge learned during ongoing work
- use `audit-memory` after writing to verify quality and drift

Do not merge these workflows into one generic memory command. Keep their shared conventions consistent.

## Resolve the Source and Destination

1. Accept a URL, provider record ID, local document, pasted text, conversation excerpt, or a source tree.
2. Use an available connector, browser, API, or local file reader when appropriate. Provider-specific tools are optional; do not require a particular MCP server or vendor.
3. Resolve the destination memory root from the user's argument or existing project context. Consider repository-local `memory/`, `.claude/memory/`, `.codex/memory/`, a platform project-memory directory, and a global memory directory only when relevant.
4. If the source or destination is ambiguous, stop and ask for the missing identifier or root. Never assume a hardcoded workspace, tenant, site, project slug, or user home path.

Record the source identity and retrieval date. Keep the original source reference whenever possible.

## Modes

Choose the narrowest mode that matches the request:

- Single source: ingest one page, file, record, or text block.
- Tree or batch: ingest a bounded set of descendants or related sources, deduplicating before writing.
- PRD or specification: preserve product intent while refining requirements into actionable project memory.
- Refresh: compare an existing source-backed memory file with current source content and propose changes.

For tree or batch work, establish a scope and maximum before fetching. Do not recursively ingest an entire provider space by default.

Use this source-type decision table:

| Source type | Retrieval rule | Extra caution |
|---|---|---|
| URL | Fetch the exact page and record access date. | Do not crawl descendants unless requested. |
| Local file | Read the supplied file and nearby referenced files only when needed. | Preserve the original path as provenance. |
| Provider record | Use the available connector or API for that record ID. | Do not assume tenant, workspace, or database names. |
| Pasted text | Treat the chat content as the source. | Avoid storing raw private content when a summary is enough. |
| Source tree | Preview the bounded file list before ingesting. | Ask before broad or recursive imports. |

## Normalize and Classify

Extract claims, decisions, requirements, constraints, interfaces, and open questions. Remove navigation noise, duplicated boilerplate, and unsupported conclusions.

Classify each result as one of the shared family types:

- `project`: product intent, architecture, workflows, requirements, decisions, and integrations
- `feedback`: explicit user or stakeholder preferences and corrections
- `reference`: stable external facts, API details, or technical background

For PRDs and specifications, preserve the source's intent but identify missing actors, states, inputs, outputs, acceptance criteria, error paths, dependencies, and measurable outcomes. Cross-check relevant repository instructions, code, and existing memory when available. Mark conflicts and unresolved assumptions instead of silently choosing a side.

## Duplicate and Refresh Checks

Before writing:

1. Read `MEMORY.md` and candidate files in the selected memory root.
2. Search by source ID, canonical URL, title, filename, and distinctive claims.
3. Decide whether the content is new, an update, a duplicate, or a conflict.
4. For refreshes, show changed sections and preserve local notes that are not contradicted by the source.

Preview the plan and ask for confirmation before overwriting existing files, resolving conflicts, writing more than three files, changing multiple relationships, or performing a broad tree import. The preview must list files to create, files to update, duplicates to skip, conflicts to preserve, and source limits. A duplicate should normally produce a report, not another file.

## Family File Standard

Use the shared memory frontmatter whenever the destination supports frontmatter:

```yaml
---
name: source-topic-name
description: One sentence describing when this memory is useful.
type: project
related: []
source: https://example.invalid/source
last_updated: YYYY-MM-DD
---
```

Use `type: project`, `feedback`, or `reference`. Keep `source` stable and append provenance notes in the body when there are multiple sources. Preserve manually maintained `related` entries. Add reciprocal relationships when a related memory is updated.

## File and Index Workflow

1. Choose a stable, descriptive kebab-case filename based on the topic, not a provider-specific object ID alone.
2. Write a focused summary with source context, durable claims, decisions, open questions, and verification notes.
3. Keep source-specific detail in a source section so the durable project knowledge remains readable if the provider changes.
4. Create or update `MEMORY.md` with one concise entry per active file.
5. Verify that indexed files exist, links resolve, and no secrets or raw private content were imported.

## Report

Return the source scope, mode, files created or updated, duplicates skipped, conflicts or open questions, and any provider or fetch limitations. Recommend `audit-memory` after a successful import or refresh.
