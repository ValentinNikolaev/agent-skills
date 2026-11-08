# GitHub Pages workflow and handoffs

## Owners and modes

| Request | Owner | Boundary |
| --- | --- | --- |
| Create, improve now, or implement selected changes | `github-pages-create` | Repository truth, stack, routes/base path, build, and separately authorized delivery |
| Propose first, let the user select, or resume approved proposals | `github-pages-improve` | Sole owner of stable `GP-` IDs and approval state, delegates execution without restarting Phase 1 |
| Content, hierarchy, labels, navigation, copy, local-search requirements | `github-pages-content` | Source freshness and reader tasks, passes URL requirements to create |
| Direction, composition, tokens, assets, themes, responsive styling | `github-pages-design` | Visual implementation in the accepted system, no hidden build or route migration |
| Audit the rendered result, report only | `github-pages-audit` | Read-only observations and advice, returns fixes to the executor |

Read the applicable sibling skill before using its procedure. The family has sibling-reference dependencies and is distributed together. A single copied folder is not a standalone installation of the complete flow. When a sibling or tool is unavailable, name the gap and perform only supported work. Do not install or alter skills as a side effect of creating a site.

## Shared envelope

Use one short block per transfer. Keep it inline for a small change. Save it in an existing project artifact only when continuation, reuse, or machine checking warrants a file.

```text
revision: commit or explicit no-Git snapshot, relevant staged/unstaged/untracked paths
working_files: relevant paths with content hashes or a retained diff/snapshot
mode_scope: task mode, allowed paths/actions, approved GP- IDs if any
owner_to: producer -> next owner
status: ready | provisional
sources: material source files/sections, inspected revisions, decision rationale
protected: content, system, behavior, route/anchor and delivery contracts in scope
unknowns: unresolved facts, evidence conflicts, unavailable capabilities
next_checks: applicable checks and what would resolve each unknown
payload: specialist result below
```

`ready` means sufficient for the named next action, not that all checks passed. `provisional` identifies inputs that cannot yet support that action. Label each significant claim as **source fact**, **rendered observation**, **tested interaction**, **assumption**, or **design judgment**. Record verification separately, using `defect`, `opportunity`, `healthy`, `not applicable` (reason), or `not verified` (missing evidence/tool).

## Specialist payloads

| Transfer | Minimum useful payload |
| --- | --- |
| Content -> Design/Create | Page purpose and reader task, canonical source and freshness, real copy/example, hierarchy/navigation, material claims and gaps, required routes/anchors including generated heading slugs |
| Design -> Create | Chosen direction and Extension/Preserve/Overhaul mode, accepted system source, needed semantic tokens/components, asset paths and provenance, responsive/motion decisions, representative preview and acceptance checks |
| Create -> Audit | Build revision and relevant working snapshot, exact build/preview commands, output directory, URL and base path, affected and legacy routes/anchors, applicable journeys, themes/viewports/states, supported tools |
| Audit -> Create/Improve | Observation with evidence type and location/state, coverage status and impact, smallest advisory correction, recheck method, remaining limitations |

For one page, nested guides, search, and changed legacy routes can be `not applicable`. Do not manufacture features to complete a handoff. A screenshot supports visual observations, not keyboard operation, successful form submission, or a link's actual destination.

## Check drift before use

Before editing from a handoff or auditing a build, compare its revision and relevant working-file snapshot with the current tree. `git status --short` alone misses later edits to an already dirty file. Include staged and untracked inputs that affect the result. Without Git, use retained files or hashes and state that limit.

When relevant inputs changed, mark the affected payload provisional and refresh only the affected sources, contracts, proposal assumptions, or build. Unrelated edits do not invalidate the whole handoff. Never apply a stale patch, overwrite user work, or audit an old build as current. Keep existing approval when the same selected scope remains valid. Ask only for a material new choice, conflict, or expansion of authorized scope.

## Continue and finish

For approved staged work, improve passes selected IDs and their disclosed prerequisites to create or the bounded specialist. Execution returns evidence to the same IDs. Audit supplies observations but never owns remediation. Rebuild after source changes that affect production output, correct confirmed in-scope defects, and rerun affected checks. Report concrete `not verified` items when tools cannot run. Never weaken sandbox, CSP, or workflow permissions to clear a design check.

Keep accepted visual decisions in the existing theme configuration, token/component source, or style guide across sessions. Separate experiments from confirmed decisions. A small authorized project artifact is enough when none exists. No automatic new memory system or `DESIGN.md` is required.

Return exact local/build/preview/publication status. Stop once the requested result and applicable verification are complete. If site work reveals a family defect, prepare a maintainer proposal with reproduction, expected behavior, affected skills, and a regression case. Do not silently edit installed skills from the site workflow.
