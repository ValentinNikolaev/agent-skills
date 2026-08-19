---
name: improve-github-pages
description: Analyze an existing GitHub Pages site and any available repository wiki, propose prioritized evidence-backed improvements, pause for explicit user approval, and then implement only the approved full or partial change set. Use for staged review-to-remediation of Pages content, navigation, accessibility, responsive layout, visual hierarchy, color scheme, typography, branding, and interactions. Do not use for a report-only audit, a net-new site, or changes the user already specified without requesting an approval gate.
---

# Improve GitHub Pages

Turn an existing Pages site into a reviewable improvement program, then apply only the changes the user selects.

## Enforce the two-phase gate

Phase 1 is read-only. Inspect, render, audit, and propose, but do not edit site files, dependencies, workflows, repository settings, or generated output. Always stop after presenting the proposal, even when the opening request broadly says to improve or redesign the site.

Phase 2 begins only after the user explicitly approves all changes or identifies approved proposal IDs. Approval to implement site changes does not authorize commit, push, publication, workflow changes, repository settings, domains, credentials, analytics, or external services unless those actions are separately named.

Do not treat “looks good,” “interesting,” or a request for explanation as implementation approval. Resolve ambiguous or conflicting selections before editing.

## Coordinate the Pages family

- Apply `audit-github-pages-ux` to collect rendered evidence and prioritize defects.
- Apply `github-pages-content-architecture` to content, hierarchy, labels, navigation, and local search proposals.
- Apply `github-pages-visual-system` to color, typography, spacing, themes, branding, and responsive proposals or implementation.
- Apply `create-github-pages` when approved work changes the framework, routes, base path, build, dependencies, or deployment.

Keep one proposal ID and one approval state across these specialist concerns.

## Read the improvement contract

Read [references/approval-and-remediation.md](references/approval-and-remediation.md) before analyzing the site or interpreting approval.

## Phase 1: analyze and propose

Establish the repository, production-equivalent build, expected Pages base path, intended readers, current routes, branding evidence, and uncommitted changes. When a GitHub Wiki exists and is available through a supplied URL, connector, or local checkout, inventory it for useful setup guidance, examples, FAQ, troubleshooting, architectural rationale, and other material missing from the Pages site. Verify wiki claims against the current repository, flag stale or conflicting pages, and prefer linking, consolidating, or importing from a maintained canonical source over blind copying. Wiki analysis remains read-only and does not authorize editing the wiki.

When rendering is possible, inspect representative desktop and narrow-mobile journeys in every supported theme. Clearly separate rendered evidence from source-only inference.

Present a prioritized change set with stable IDs. Each proposal must include observed evidence, the concrete change, expected reader benefit, affected scope, risk, and verification. Show color or theme changes as semantic token mappings and rendered-use examples rather than an unexplained palette.

End with an explicit approval prompt such as:

> Approve all proposals, approve selected IDs such as `GP-01, GP-04`, request revisions, or decline. No files have been changed.

Then stop.

## Phase 2: implement the approved scope

Before editing, re-check repository status and the proposal assumptions. If the site or overlapping files changed after the proposal, explain the drift and refresh affected proposals rather than applying stale edits.

Implement only approved IDs and their necessary disclosed prerequisites. Preserve unapproved behavior, public routes, branding, canonical content, user changes, and deployment configuration. If an approved item becomes materially broader during implementation, stop and request approval for the expansion.

Run applicable production builds, link and route checks, and rendered verification. Report implemented IDs, deviations, verification evidence, unapproved proposals left untouched, and any separately authorized delivery status.
