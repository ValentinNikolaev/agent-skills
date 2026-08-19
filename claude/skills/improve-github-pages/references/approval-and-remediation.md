# GitHub Pages approval and remediation contract

## Contents

- [Phase 1 evidence](#phase-1-evidence)
- [Wiki evidence](#wiki-evidence)
- [Audit scope](#audit-scope)
- [Design opportunity evidence](#design-opportunity-evidence)
- [Proposal format](#proposal-format)
- [Approval states](#approval-states)
- [Implementation controls](#implementation-controls)
- [Handoff](#handoff)

## Phase 1 evidence

Use the strongest available evidence in this order:

1. rendered behavior from the production build under the expected Pages base path;
2. repository instructions, site configuration, theme code, content, tokens, assets, and tests;
3. an available repository GitHub Wiki, checked against current repository evidence;
4. current public site behavior when access is supplied and authorized;
5. clearly labelled inference when rendering or project evidence is unavailable.

Record the inspected commit or working tree state, build command, output, preview URL, viewports, themes, browser, and unavailable tools. Do not describe source inspection as visual, keyboard, contrast, or screen-reader verification.

## Wiki evidence

When a GitHub Wiki is available, inventory its pages and identify material that could improve the Pages site: installation details, worked examples, FAQ, troubleshooting, limitations, migration notes, or maintained architectural explanations.

- Compare commands, versions, configuration, links, and behavior with the current repository before recommending reuse.
- Mark useful material as current, needs verification, stale, conflicting, duplicated, or uniquely valuable.
- Prefer a single maintained source. Recommend linking, consolidating, generating, or carefully adapting rather than creating another unsynchronized copy.
- Treat wiki provenance and attribution as content requirements.
- Keep wiki edits out of the approved Pages implementation unless the user separately authorizes that external write.
- If the wiki is known to exist but cannot be accessed, list it as an evidence gap instead of assuming it contains nothing useful.

## Audit scope

Cover only areas supported by the site and request:

- reader journeys, content accuracy, hierarchy, navigation, search, and 404 behavior;
- visual hierarchy, information density, layout, typography, spacing, icons, imagery, and brand consistency;
- semantic color roles, foreground/background contrast, focus, light/dark themes, and non-color cues;
- responsive reflow, mobile navigation, tables, code, long strings, media, zoom, and touch targets;
- keyboard order, labels, alternatives, reduced motion, feedback, and interactive states;
- base-path assets, anchors, nested routes, legacy links, dependencies, and performance issues when they affect the experience.

Do not propose arbitrary novelty. Simplicity is not itself a defect, but a generic or under-expressive visual system may justify an enhancement when a more distinctive direction would improve project identity, comprehension, trust, or reader engagement. Preserve a coherent existing system when targeted fixes or restrained refinement provide the stronger outcome.

## Design opportunity evidence

Run design exploration separately from defect discovery so usable but visually under-realized sites still receive a fair assessment. Consider:

- whether the framework's default theme obscures the project's identity;
- whether hierarchy, typography, composition, imagery, or interaction undersell the content;
- whether repository logos, diagrams, screenshots, terminology, domain metaphors, or other maintained assets support a distinctive direction;
- whether restrained, distinctive, and bold directions offer materially different reader outcomes;
- whether current external references reveal a transferable pattern that fits the repository rather than a fashion to copy.

An opportunity needs repository or reader-task support, but it does not need a broken interaction. Generate alternatives as exploration, then report only the strongest viable directions. Label external references and distinguish observed patterns from the proposed adaptation.

## Proposal format

Assign stable IDs such as `GP-01` and do not renumber them after presentation. For each proposal provide:

- **Area and severity:** critical, major, minor, or enhancement;
- **Evidence:** route, viewport/theme, element, and observed behavior or source-backed limitation;
- **Change:** a concrete before/after description;
- **Benefit:** the reader task or accessibility/usability outcome;
- **Scope:** affected pages, components, tokens, assets, files, dependencies, routes, or workflow;
- **Risk:** migration, branding, compatibility, content, privacy, or maintenance tradeoff;
- **Verification:** observable proof that the change works;
- **Dependencies:** other proposal IDs that must be approved with it.

Group proposals into quick corrections, visual/content improvements, and structural changes when that makes selection easier. Offer alternatives only for a real design choice; state a recommendation and tradeoff instead of presenting cosmetic variants without judgment.

For color proposals, show semantic roles such as background, surface, text, muted text, border, action, focus, code, success, warning, and danger. Derive them from repository branding when possible and include contrast evidence for actual rendered pairings. Avoid introducing remote fonts, trackers, hosted assets, or analytics as visual improvements.

For bold visual proposals, also include:

- **Boldness:** restrained, distinctive, or bold;
- **Current ceiling:** what the present design communicates well and what it fails to express;
- **Concept:** one coherent visual direction rather than a bag of component tweaks;
- **Repository evidence:** the assets, vocabulary, product behavior, audience, or domain cues supporting it;
- **System impact:** affected color, type, spacing, grid, components, imagery, motion, and responsive rules;
- **Preview plan:** the smallest representative mockup or rendered slice needed before full implementation.

End Phase 1 with a compact coverage matrix for reader journeys, content, navigation, visual hierarchy, typography, color and themes, spacing and layout, imagery and branding, responsive behavior, accessibility, and interactions. Use `defect`, `opportunity`, `healthy`, `not applicable`, or `not verified`, and give a short reason. The matrix is an accountability record, not a source of forced proposals.

## Approval states

Accept these as explicit approval:

- all proposal IDs;
- a listed subset of IDs;
- a clearly named option within a proposal;
- an explicit rejection of the remainder.

Ask for clarification when an approved item has unapproved dependencies, the user selects mutually exclusive options, or wording does not identify a scope. Suggestions, questions, praise, and requests to compare options leave every proposal pending.

After partial approval, keep unapproved items pending or declined as the user states. Do not silently include convenient neighboring changes.

## Implementation controls

- Re-check status and assumptions before writes.
- Map every edit to an approved proposal ID.
- Make prerequisites visible; do not hide scope expansion as refactoring or cleanup.
- Preserve routes, anchors, `CNAME`, base path, canonical documentation, lockfile discipline, and user changes.
- Do not add or upgrade dependencies unless an approved proposal disclosed them.
- Do not change deployment or publish without separate authorization.
- Validate each approved item using its stated verification method.

If an approved change fails verification, attempt only safe in-scope correction. Stop when resolution requires a new dependency, broader migration, external account, credential, publication action, or material change to an unapproved area.

## Handoff

Report:

- approved and implemented IDs;
- approved IDs not completed and why;
- pending or declined IDs left unchanged;
- files, dependencies, routes, and workflows changed;
- static, build, rendered, and accessibility checks actually performed;
- remaining limitations and any separate delivery step awaiting authorization.
