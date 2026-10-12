# Composition critique and recurring failure patterns

## Contents

- [Critique from evidence](#critique-from-evidence)
- [Contextual failure patterns](#contextual-failure-patterns)
- [Report and boundaries](#report-and-boundaries)

## Critique from evidence

Use a rendered page or supplied screenshot for composition judgments. Record route, viewport, theme, and relevant state when available. A screenshot supports static visual observations only; source-only concerns remain hypotheses until rendered. Inspect these dimensions against the actual brief:

| Dimension | Check |
| --- | --- |
| Coherence | Type, colors, shapes, assets, density, and motion support the stated direction and project identity |
| Hierarchy | The first visual entry point and reading order support the reader's task; metadata and decoration do not compete |
| Craft | Alignment, grouping, spacing, image crop, and responsive reflow are deliberate across real content |
| Purpose | Each element explains, navigates, provides feedback, or identifies something; removing decoration does not impair the task |
| Expression | Project-specific evidence gives the site character without weakening familiar navigation or readability |

On documentation pages prioritize finding and understanding information. On a project landing page, identity and expression can take a larger role. Do not impose aesthetic scores, headline/body ratios, a fixed whitespace percentage, a maximum font count, or a mandatory number of fixes.

## Contextual failure patterns

These are diagnostic prompts, not prohibitions. An established brand pattern or a reader-task benefit can justify an apparent exception. Report only consequential examples.

| Pattern | Observable evidence | Smallest useful correction |
| --- | --- | --- |
| Mechanical section rhythm | Most sections repeat the same low-information label, heading, paragraph, or mirrored split | Remove redundant labels and vary composition according to content roles |
| Excessive card containers | Unrelated cards surround every paragraph or item without a grouping or interaction reason | Use alignment, spacing, dividers, or a shared surface where they convey the relationships better |
| Empty geometric layout | Bento cells or arbitrary spans exist only to complete a shape | Let meaningful content determine cells and prominence; remove filler |
| Unsupported hero formula | A large centered slogan, gradient, and competing CTAs obscure the actual project and next task | Bring real examples, screenshots, or a concrete proposition forward; distinguish actions |
| Decorative metadata | Fake status dots, coordinates, counters, version labels, or badges imply state or credibility without evidence | Remove them or connect them to verified information |
| Shape or token drift | Similar components use incompatible radii, borders, spacing, or unrelated colors without a semantic reason | Consolidate through the existing token and component roles |
| Counterfeit assets | CSS shapes or invented captures stand in for a recognizable real logo or product interface | Use verified assets, an honest preview slot, or an appropriate text identity |
| Media or decoration overwhelms reading | Labels cover meaningful imagery, display text clips, or textures hide content | Simplify treatment, adjust hierarchy and crop, and preserve readable captions |
| Spectacle without purpose | Multiple loops, reveals, or pinned sections delay reading without adding explanation or feedback | Remove or reduce motion and provide an equivalent reduced-motion path |
| Marketing treatment on reference pages | Giant headings and excessive spacing hinder lookup, comparison, or scanning | Restore task-appropriate density and a stable navigation/content structure |
| Happy-path-only styling | Search, menu, theme, or copy controls look complete only in one success state | Inspect applicable focus, active, disabled, empty, error, and narrow-layout states |

Do not ban gradients, system fonts, accent-bordered callouts, emoji, or repeated components categorically. Evaluate whether they suit existing branding, communicate real information, and remain readable. Consistency across documentation pages is often a strength.

## Report and boundaries

Return a concise **Keep / Fix / Opportunity** assessment. For each actionable item state observed evidence, the affected reader task or visual intent, a concrete correction, and a verification method. Separate functional/accessibility defects from supported design opportunities and subjective preferences. Do not infer a verified interaction or contrast result from how a screenshot looks.

This composition pass does not replace the production-build, keyboard, responsive, contrast, or route checks owned by `audit-github-pages-ux`. In a read-only audit, advise without editing. In `improve-github-pages`, attach supported opportunities to the shared proposal IDs and approval state. During implementation, correct in-scope problems and disclose a material scope expansion before pursuing it.
