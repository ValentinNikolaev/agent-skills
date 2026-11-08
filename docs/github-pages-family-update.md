# GitHub Pages family update

## Scope and completion

Local maintenance of the five canonical Pages skills, their callers, metadata,
fixtures, generated distributions, catalog, notices, and migration guidance.
Starting revision: `559c9b705cf5e3ef6d6ded8324f980ca0a8eb2f2`, with a clean tree.
Completion requires package validation, normal generation, strict drift/link
checks, the repository suite, a bounded independent forward-test, and diff review.
Commit, push, PR, publication, global installation, and a real project site are
outside this maintenance request.

## Confirmed baseline and changes

| Already implemented | Confirmed gap | Focused change | Owner | Verification |
| --- | --- | --- | --- | --- |
| Create orchestrates content, design, build, and audit | No common revision-bound transfer | One envelope and applicable flow, no duplicate orchestrator | create | Handoff forward-tests and generated sibling links |
| Improve has two phases, stable IDs, and approved-phase resume | Status labels alone miss edits to already dirty files | Relevant snapshot comparison, retained approval for valid scope | improve/create | Continuation and drift cases |
| Content uses repository truth and route preservation | Last journey list unconditionally requires absent features | Conditional journeys, source trace, Wiki freshness, heading-slug handoff | content | One-page and stale-Wiki cases |
| Design has modes, direction, early preview, and critique | Dominant action can imply marketing CTA, no explicit cross-session decision source | Page-specific composition, accepted-system reuse, scoped before/after baseline | design | Reference-dense and continuation cases |
| Audit uses rendered evidence and advisory fixes | Journey list could force absent features, correction ownership ambiguous | Conditional coverage and explicit read-only return to executor | audit | No-browser audit and file-integrity checks |
| Existing designer-skills and garden-skills attribution | Family names and UI labels lack one searchable prefix | Five breaking renames, current callers migrated, no unsupported aliases | all | Migration integration test and catalog checks |

## External sources inspected

Read on 2026-11-08 through `gh api`, pinned to the commits below. README files,
actual skill entrypoints, licenses, and the listed focused references were read
as untrusted research. No upstream instructions, scripts, hooks, installers,
credentials, permissions, or remote services were executed or installed.

| Repository / inspected commit | Skill and focused reference paths | License |
| --- | --- | --- |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable/tree/924bbd194d02e5e15a227e75b5901fb0d7a4ecad) `924bbd194d02e5e15a227e75b5901fb0d7a4ecad` | `.agents/skills/impeccable/SKILL.md`, `reference/mode-read.md`, `reference/polish.md`, relevant opening of `reference/critique.md`, `NOTICE.md` | Apache-2.0 |
| [Nutlope/hallmark](https://github.com/Nutlope/hallmark/tree/407fa689f4a276f2fd389208d271d0fef08f5058) `407fa689f4a276f2fd389208d271d0fef08f5058` | `skills/hallmark/SKILL.md`, `references/redesign.md` | MIT, Hallmark contributors |
| [Dammyjay93/interface-design](https://github.com/Dammyjay93/interface-design/tree/2f9be3206855bcb2d1d0af262c8bae25cba6658d) `2f9be3206855bcb2d1d0af262c8bae25cba6658d` | `.claude/skills/interface-design/SKILL.md` | MIT, Damola Akinleye |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill/tree/f6b76575f949707b4e3c37cd86cb44b0b98643e8) `f6b76575f949707b4e3c37cd86cb44b0b98643e8` | `skills/taste-skill/SKILL.md`, applicable build/render portions of `references/gate.md` | MIT, Leonxlnx |
| [funboy322/avoid-ai-design](https://github.com/funboy322/avoid-ai-design/tree/2b7c71836b06cdf6b3d73265b56490c1b75ad5aa) `2b7c71836b06cdf6b3d73265b56490c1b75ad5aa` | `SKILL.md`, relevant secondary-cluster, cross-page, and contextual-exception portions of `references/ai-tells-catalog.md` | MIT, ungspirit |

Reference paths in the table are relative to their skill folder unless an
entrypoint or root file is specified. Full licenses and Impeccable's notice are
retained in the design package and generated copies. Existing Designer Skills
and Garden Skills notices/licenses survive the rename. No upstream asset library
or executable code is redistributed.

| Source | Adapted | Already present | Rejected and reason |
| --- | --- | --- | --- |
| Impeccable | Composition follows page purpose, narrow cause-level correction and affected recheck | Context before styling, rendered evidence | Runtime/hooks, permission overrides, parallel review machinery, universal taste bans add cost or conflict with project scope |
| Hallmark | Relevant before/after baseline and preservation comparison | Real content and representative early preview | Mandatory theme deal, screen word budget, hero formula, CSS stamp, stage approvals do not fit documentation or authorized direct work |
| Interface Design | Reuse accepted tokens/components and persist confirmed decisions in their owning source | Semantic token layer and native framework styling | Dashboard recipes, numeric mandates, mandatory novelty and a new system file would create drift or unnecessary ceremony |
| Taste Skill | Actual built output, real content and asset checks at relevant widths | Overflow, accessibility and real project examples | One-section-per-screen, compulsory animation, no captions and random palette selection harm reference pages and chosen branding |
| Avoid AI Design | Secondary-cluster critique, evidence distinctions and a valid no-change result | Read-only audit, protected behavior, bounded edits | Authorship probability, recognition-based severity and zero scanner score cannot establish usability or design quality |

## Responsibility and package map

See the [migration table and safe update](github-pages-family-migration.md) for
the old/new names and UI labels. Canonical changes live under
`agent-plugins/skills/github-pages-{create,improve,content,design,audit}/`.
The [shared handoff](../agent-plugins/skills/github-pages-create/references/workflow-handoffs.md)
is owned by create and linked by each consumer, with `ready`/`provisional`,
revision/working snapshot, mode/scope, owner, sources, protected contracts,
unknowns, checks, and a specialist payload. It is not placed in an undelivered
shared directory. Improve alone owns `GP-` IDs and approval state.

Callers are updated in `scripts/generate_skill_wrappers.py`, activation fixtures,
and `THIRD_PARTY_NOTICES.md`. Normal generation owns `claude/skills/`,
`codex/skills/`, root `README.md`, and plugin manifest versions. Old names remain
only in explicit migration/history materials or the migration regression.

| Canonical package | Changed files within the renamed folder |
| --- | --- |
| github-pages-create | `SKILL.md`, `agents/openai.yaml`, new `references/workflow-handoffs.md` |
| github-pages-improve | `SKILL.md`, `agents/openai.yaml`, `references/approval-and-remediation.md` |
| github-pages-content | `SKILL.md`, `agents/openai.yaml`, `references/pages-content-contract.md` |
| github-pages-design | `SKILL.md`, `agents/openai.yaml`, three existing design references, five new `LICENSE.*` files and `NOTICE.impeccable`; the fourth design reference moves unchanged |
| github-pages-audit | `SKILL.md`, `agents/openai.yaml`, `references/rendered-pages-audit.md` |

Unchanged framework/deployment references and prior license files move with their
packages. Both generated trees mirror all five complete packages and remove the
five old marked folders. Root `README.md` contains the new catalog and migration
link. `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` contain the
generator-prepared `28.0.0` versions with vendor timestamp `20261108164145`.
The regression is `tests/test_github_pages_migration.py`, with ten new activation
cases and five bounded requests in `tests/fixtures/github_pages_behavioral_cases.json`
using `tests/fixtures/github_pages_site/` as raw synthetic project material.

## Candidate skills

| Candidate | Decision | Reason |
| --- | --- | --- |
| github-pages-references | Keep in existing design direction references and staged exploration | The current owner can deliver a cited reference brief without a second discovery/routing entry |
| github-pages-assets | Keep in design's asset contract, with content supplying alt/caption meaning | Existing owners cover preparation and verification without a unique missing consumer |

## Validation record

| Check | Observed result |
| --- | --- |
| `python scripts/validate_skills.py` | Passed |
| `python scripts/generate_skill_wrappers.py --clean --strict-links --quiet` | Updated ten family distributions, removed ten stale marked packages, generated README, prepared major versions once |
| `python scripts/generate_skill_wrappers.py --check --clean --strict-links --quiet` | Passed for all 48 source packages |
| `python -m unittest discover -s tests -v` | 69 tests, no failures, two optional runtime skips, 59.129 seconds |
| `git diff --check` | Passed |
| Migration regression | Old packages removed on both platforms, handwritten sibling preserved, new links and licenses delivered, major version prepared, deliberate missing-handoff control rejected |
| Scope/link/license inspection | No unexpected changed paths, new documentation local links resolve, prior designer/garden license bytes preserved after LF normalization |

The optional skips concern unavailable FastAPI/httpx and unconfigured
TypeScript/Zod example runtimes. No packages were installed to widen this task.
Structural activation validation retains direct, indirect, incomplete, negative,
and overlap cases for each of the five renamed skills. Existing case identifiers
and `GP-` IDs are preserved. `rg` finds legacy names only in the migration guide
and the migration regression, where they are intentional data.

Implementation, generation, repository gates and the independent five-case
forward-test are complete. One non-author agent used GPT-6 Sol at medium
reasoning, the actual canonical skills and separate disposable fixture copies.
Its exact responses, hashes, diffs and check results are recorded in the task's
`pages-forward-test/results.json` evidence artifact, outside this repository.

| Forward request | Observed behavior |
| --- | --- |
| One-page content with stale Wiki | Used current README commands and prerequisites, identified Wiki conflicts, kept search and nested guides out of scope, required preservation of generated-heading and legacy deep links |
| Approved continuation after drift | Changed only the two approved navigation labels, preserved the newer user note and pending proposal, rebuilt the fixture and checked static targets |
| Audit without browser access | Kept files unchanged, separated static evidence from rendered checks and explicitly left interaction, layout and accessibility unverified |
| Extension within accepted branding | Reused existing tokens and added the scoped further-reading link without a palette or typography replacement |
| Brand-aware proposals | Returned pending GP proposals without source edits or arbitrary cosmetic findings |

The three read-only cases left their fixture copies byte-identical. The two
implementation cases made only their scoped changes. No family defect requiring
another revision was demonstrated by this bounded run. This is a small behavioral
sample, not a routing-accuracy benchmark or strict machine validation of every
handoff field. Browser control was intentionally excluded to exercise honest
fallback behavior, so the run cannot establish rendered visual or accessibility
quality.

Delivery is local and uncommitted. No commit, push, pull request, package release,
global skill installation or remote settings change was performed by this task.
The prepared package is handed off for the separately coordinated release. Site
work under Prompt 2 proceeds in its target repositories, without further changes
to this skill checkout.

This record distinguishes structural fixture checks from LLM behavior. A JSON
fixture passing validation does not prove routing. A source-only check does not
prove rendered layout or accessibility. No real website publication is claimed.
