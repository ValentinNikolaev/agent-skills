---
name: github-pages-audit
description: Audit a rendered GitHub Pages site or production-equivalent build and report UX and accessibility findings without edits. Use for Pages verification, not source-only review or implementation.
---

# GitHub Pages: Audit

Evaluate the rendered Pages experience against repository evidence and real reader tasks. This pass stays read-only. Return requested fixes to `github-pages-create`, or to `github-pages-improve` for its existing proposal/approval state.

## Establish the audit target

- Confirm the site is GitHub Pages or a production-equivalent local build with the same base path and output.
- Resolve the repository/build path and preview URL before testing. If the rendered target cannot be identified or started safely, request that target and report the audit as not run rather than substituting source inspection.
- Inspect repository branding, documented reader tasks, current site configuration, route expectations, and any explicit design tokens or content rules.
- Record the exact build, URL or local preview, viewport sizes, theme, browser, and available accessibility tooling.
- Check the build against the current relevant source snapshot using the family's [handoff contract](../github-pages-create/references/workflow-handoffs.md). Build or preview in a disposable directory when an audit requires generated files, preserving site sources and tracked output.
- Do not claim rendered, keyboard, contrast, or screen-reader verification when only source files were inspected.

## Read the checklist

Read [references/rendered-pages-audit.md](references/rendered-pages-audit.md) before performing the audit.

For visual coherence and repeated composition patterns, use the visual specialist's [composition critique](../github-pages-design/references/design-critique.md) as a supplemental pass on the same rendered evidence. Keep usability defects, supported design opportunities, and subjective preferences distinct. This pass does not replace the audit checklist or authorize edits.

## Audit representative journeys

Cover home and the primary reader task, then only features that exist or change:

1. home or landing page;
2. primary first-success journey;
3. one nested documentation page;
4. one code-, table-, image-, or reference-heavy page;
5. navigation and search when present;
6. not-found, empty, or zero-results behavior;
7. light/dark themes and narrow/desktop widths when supported.

Traverse interactive elements with a keyboard and inspect visible states, not screenshots alone.

Mark absent features `not applicable` with a reason. Do not add nested docs, search, a second theme, or legacy routes to satisfy this list. When browser/runtime access is unavailable, applicable rendered checks remain `not verified`, not healthy.

## Report only actionable findings

For every defect include:

- **Evidence:** page, viewport/theme, element, and observable behavior;
- **Impact:** blocked reader task or accessibility/usability consequence;
- **Severity:** critical, major, minor, or enhancement;
- **Fix:** the smallest advisory correction consistent with the existing stack and tokens; recommending it does not authorize an edit;
- **Verification:** how to prove the correction worked.

Order findings by user impact, then confidence. Separate confirmed defects from limitations and unverified checks. Do not treat automated accessibility output as certification.

Return the shared audit payload and coverage statuses even when no defects survive. Distinguish source facts, rendered observations, tested interactions, assumptions, and design judgments. A healthy or no-change result is valid, with no quota of findings.
