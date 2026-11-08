# GitHub Pages family migration

This is a breaking skill rename. The prepared local packages use these names.
They are available to installed users only after the corresponding release is
published and their installation is updated. This document does not establish
publication or update any global installation.

| Previous name | Canonical name | UI label |
| --- | --- | --- |
| `create-github-pages` | `github-pages-create` | GitHub Pages: Create |
| `improve-github-pages` | `github-pages-improve` | GitHub Pages: Improve |
| `audit-github-pages-ux` | `github-pages-audit` | GitHub Pages: Audit |
| `github-pages-content-architecture` | `github-pages-content` | GitHub Pages: Content |
| `github-pages-visual-system` | `github-pages-design` | GitHub Pages: Design |

No aliases or compatibility copies are provided. Old invocations do not
automatically resolve to new names. Existing `GP-` proposal IDs and their
approval state remain valid when their underlying scope is still current.

## Update safely

1. Identify whether the installed family is plugin-managed or manually copied.
   Inspect local modifications before replacing files. Back up modified skills
   outside the installation or retain their diff for deliberate reconciliation.
2. For a managed plugin, use that manager's normal update route after publication.
   Do not hand-edit its cache or assume the unpublished checkout is installed.
3. For manual copies, copy the complete updated family from the generated
   `codex/skills/` or `claude/skills/` tree to the corresponding installation.
   The family uses sibling references, so one folder alone does not supply the
   complete creation flow. Preserve the included licenses and notices.
4. Inspect and explicitly retire only the five obsolete managed/copied folders
   once local changes are reconciled. Do not delete other skills. Repository
   generation's `--clean` cleans marked output in this checkout, not arbitrary
   global installations or user-modified copies.
5. Update explicit `$skill-name` calls, saved prompts, project instructions, and
   automation references using the table above. Refresh the host's skill catalog
   by its supported reload route and verify the five new UI labels and calls.

The canonical source remains `agent-plugins/skills/`. Maintainers regenerate both
distributions with the documented repository checks. The generator prepares a
major version when old packages are removed. Subsequent repair generation for
that prepared release uses `--no-version-bump`.

## Choose the flow

```text
Use $github-pages-create to create or improve this repository's Pages site now.
Preserve verified facts, public URLs, and user work. Deliver a local result.

Use $github-pages-improve to propose changes first. Give proposals GP- IDs and
wait for my selection before editing site sources.

Use $github-pages-audit to check this production-equivalent rendered Pages build
and report evidence and limitations without editing.
```

For a bounded content or visual task, invoke `$github-pages-content` or
`$github-pages-design` directly. Provide the target repository and requested
change. Site authoring alone does not authorize delivery changes or publication.
On continuation, preserve approved selections and compare current inputs with
the [shared handoff](../agent-plugins/skills/github-pages-create/references/workflow-handoffs.md)
before using an earlier result.
