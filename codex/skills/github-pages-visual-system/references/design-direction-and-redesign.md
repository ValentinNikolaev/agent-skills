# Design direction and redesign

## Contents

- [Design brief](#design-brief)
- [Change modes](#change-modes)
- [Protected contracts and assets](#protected-contracts-and-assets)
- [Preview and implementation](#preview-and-implementation)

## Design brief

Record the following before choosing colors or components. Infer from repository evidence and the request; ask a focused question only when missing information would materially change the result.

| Decision | Record | Visible consequence |
| --- | --- | --- |
| Audience and task | Who reads the site and what they should accomplish | Entry point, reading order, prominence of the next action |
| Visual language | A specific direction supported by project identity | Composition, type character, image treatment, and hierarchy |
| Compositional variation | Familiar, distinctive, or experimental | Stable documentation grid versus an expressive landing section |
| Motion | Static, feedback-only, or purposeful narrative | State transitions and reduced-motion behavior; no scroll hijacking |
| Information density | Reading-led, balanced, or reference-dense | Content width, grouping, table treatment, and navigation depth |
| Asset dependence | Which real images or diagrams explain or identify the project | Asset inventory and layout priorities before ornamental CSS |
| Brand fidelity | Which existing cues must match and which may evolve | Reuse of logos, tokens, icons, component shapes, and voice |

Use qualitative choices with explicit consequences rather than numerical taste scores. A dense reference page needs stable scanning even when the landing page is expressive. Keep narrative motion out of long technical reading. Accessibility and accurate content constrain every choice.

## Change modes

| Mode | Scope | Preserve |
| --- | --- | --- |
| Extension | Add or adjust a bounded component inside the current visual system | Existing type, tokens, density, states, and component vocabulary; new work should look native |
| Preserve | Develop the current identity through targeted improvements | Recognizable branding, content, navigation, routes, and working behavior |
| Overhaul | Introduce an agreed new visual language | Reader tasks, accurate content, public and behavioral contracts, and the explicitly retained brand cues |

For a new site, establish a new direction from repository evidence without inventing an existing identity. For an existing site, an overhaul does not authorize framework migration, route changes, or removal of content. Hand content restructuring to `github-pages-content-architecture` and build or routing changes to `create-github-pages` within the authorized scope.

Record a short before/after plan: mode, keep, improve, remove, protected contracts, highest-risk change, and fallback. Repair functional failures, hierarchy, spacing, and state feedback before replacing viable components. In a Preserve or Extension task, stop once the requested result is met.

## Protected contracts and assets

Inventory applicable contracts before visual changes:

- routes, slugs, anchors, navigation, search, and legacy deep links;
- informative content, code examples, legal text, translations, and public metadata;
- keyboard order, semantics, focus, accessible controls, and reduced-motion behavior;
- forms, validation, submission behavior, component APIs, selectors, and persistent-state keys;
- existing analytics identifiers when present; their preservation does not authorize adding analytics;
- identity-bearing logos, wordmarks, screenshots, diagrams, and documented brand rules.

Use repository assets or appropriately licensed official material. Record source, local path, rights, role, and supported theme for reused assets. Never recreate an actual product screenshot or logo with decorative shapes, or invent adoption metrics. Original diagrams and CSS illustrations are appropriate when clearly explanatory rather than presented as real product evidence.

A text wordmark is valid when the project uses it or has no established logo. A missing nonessential asset does not block the whole task: omit it or disclose a preview slot. Resolve missing identity-critical material when it determines the requested direction. Preserve user content and technical contracts unless their change is included in the authorized scope.

## Preview and implementation

Use the smallest representative slice that resolves the design uncertainty: the landing proposition and one content-rich documentation section, or the specific component being extended. Test real long headings, code, navigation, and narrow widths. Show a supported theme as well as the primary theme when theme differences affect the choice.

- During `improve-github-pages` Phase 1, keep analysis read-only. Provide an inline concept, an annotated existing render, or a preview plan within the shared proposal IDs; do not write site files or generated output to make a prototype.
- During authorized implementation, produce an early local preview, explain assumptions, and continue within the approved scope. Await feedback only when the user requested a checkpoint or a material unresolved choice requires it.
- For visual comparison, a side-by-side sample is often sufficient. Add a parameter panel only when requested or necessary to resolve a specific choice; keep preview controls out of production output.
- Deliver maintainable framework-native styling. Keep current dependencies unless a justified change was authorized. Do not introduce CDN React/Babel, remote fonts, or animation libraries merely to reproduce a reference.

At delivery, remove preview placeholders, verify preserved contracts and real content, and report actual build, rendered, and accessibility checks. Source inspection cannot establish visual acceptance.
