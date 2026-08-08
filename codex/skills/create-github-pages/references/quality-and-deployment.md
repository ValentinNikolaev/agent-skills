# Quality and deployment contract

Apply the relevant sections while implementing and verifying the site. Adapt commands to the selected stack and current official documentation.

## Contents

- [Content integrity](#content-integrity)
- [Dependencies and public resources](#dependencies-and-public-resources)
- [Navigation and hierarchy](#navigation-and-hierarchy)
- [Route and migration integrity](#route-and-migration-integrity)
- [Search and interactive content](#search-and-interactive-content)
- [Responsive and accessible behavior](#responsive-and-accessible-behavior)
- [Conditional GitHub Pages workflow](#conditional-github-pages-workflow)
- [Commit-driven updates](#commit-driven-updates)
- [AI refresh opt-in](#ai-refresh-opt-in)
- [Static and build verification](#static-and-build-verification)
- [Rendered browser verification](#rendered-browser-verification)
- [Final diff review](#final-diff-review)

## Content integrity

- Trace installation commands, examples, configuration keys, API signatures, version support, and status claims to current repository files.
- Prefer links to canonical changelog, contribution, security, and license files over copied prose.
- Remove template filler, fictional metrics, fake testimonials, unsupported badges, dead navigation, and empty pages.
- Confirm public examples expose no credentials, internal hosts, personal paths, private data, or unsafe defaults.
- Make the first successful user task complete and internally consistent.
- Preserve quotations, licenses, attribution, and provenance when adapting existing material.

## Dependencies and public resources

- Consult current official documentation whenever adding or materially changing frameworks, runtimes, plugins, actions, or search integrations.
- Confirm maintained status and compatibility with the repository's supported runtime.
- Honor the committed lockfile with a frozen or lockfile-verifying install command.
- Avoid duplicate package managers and review lockfile changes.
- Review package provenance, license, install scripts, transitive cost, and maintenance burden.
- Prefer reviewed self-hosted assets for stable public resources.
- When a remote resource is justified, document privacy, availability, versioning, and integrity implications; use available integrity controls for immutable assets.
- Do not add analytics, trackers, hosted search, remote fonts, or other third-party requests without explaining operational and privacy effects.

## Navigation and hierarchy

- Use one H1 per page, followed by H2 and H3 without unexplained jumps.
- Keep primary navigation short and stable.
- Provide sidebar or section navigation for multi-page docs and a table of contents for long pages when supported.
- Keep current location visible and make previous/next links meaningful.
- Ensure the logo and site title return to the site home rather than unexpectedly opening the source repository.

## Route and migration integrity

Before changing framework, content root, slug rules, or base path:

1. inventory existing routes, anchors, asset URLs, canonical URLs, and custom-domain behavior;
2. derive legacy routes from the current site output, configuration, sitemap, or documented public URLs;
3. map each route to a preserved destination, redirect, or documented intentional removal;
4. preserve the mapping in a reviewable route/redirect manifest when the migration is material;
5. test representative home, nested, deep-link, anchor, asset, and not-found cases under the production base path.

Do not equate a successful new build with preserved public URLs.

## Search and interactive content

- Prefer a maintained local search integration when content can be indexed at build time.
- Use hosted search only when cost, credentials, indexing, privacy, and availability are justified.
- Verify search is keyboard reachable, labelled, and capable of finding representative terms without a full reload.
- Exclude irrelevant generated pages and duplicates from the index when supported.
- Verify rendered code blocks expose a keyboard-accessible copy action and readable feedback.
- Label code languages when known and prevent horizontal page overflow.
- Render notes, tips, warnings, dangers, and cautions with text or icons as well as color.
- Make tabs keyboard accessible and keep their content discoverable.

## Responsive and accessible behavior

At a narrow mobile viewport and a typical desktop viewport, verify:

- navigation, headings, tables, code, search, and corner/source elements do not clip;
- the mobile menu opens, traps no focus, closes predictably, and exposes essential links;
- keyboard order is logical and focus is visible;
- text and control contrast remains usable in light and dark themes;
- informative images have descriptive alternatives and decorative images have empty alternatives;
- icon-only controls have labels;
- zoom, touch targets, and horizontal scrolling remain usable;
- decorative transitions respect reduced-motion preferences;
- no essential information depends only on color, hover, or animation.

Use an available accessibility audit as supporting evidence, not certification.

## Conditional GitHub Pages workflow

Create or change a workflow only when the user requests deployment, commit-driven updates, delivery repair, or Pages configuration. Site authoring alone does not authorize CI changes.

When delivery is in scope, follow the current official Pages custom-workflow pattern and verify:

- checkout, runtime, and Pages actions use currently maintained releases confirmed in official documentation;
- dependency installation honors the lockfile and fails on drift;
- the production build matches local verification;
- Pages configuration occurs before a build that needs its computed base URL;
- the uploaded artifact is the actual output directory;
- permissions are limited to the required `contents: read`, `pages: write`, and `id-token: write` capabilities;
- deployment uses the `github-pages` environment and exposes the URL when supported;
- concurrency prevents overlap without needlessly cancelling an active deployment;
- triggers use the real default branch and relevant paths;
- manual dispatch supports recovery;
- only one workflow owns production deployment.

Never copy action versions from memory when official documentation is available.

## Commit-driven updates

When requested, ensure relevant commits deterministically rebuild the site. Path filters must cover:

- site configuration and theme files;
- documentation and Markdown inputs;
- imported README or reference sources;
- package manifest and lockfile;
- documentation generators and schemas;
- route/redirect manifests;
- the deployment workflow.

Omit path filters when reliable coverage is difficult. A redundant build is safer than a stale public site.

## AI refresh opt-in

Create AI-authored refresh automation only after explicit authorization. Require:

- a documented source-of-truth boundary and allowlisted outputs;
- least-privilege secrets and permissions;
- pinned or supply-chain-controlled dependencies;
- versioned prompt and model configuration;
- deterministic post-generation validation;
- a branch or pull request for human review rather than direct production writes;
- recursive-loop prevention;
- concurrency and spend controls;
- failure behavior that leaves the last verified site live.

Keep deterministic Pages builds usable without AI credentials.

## Static and build verification

Run every applicable check supported by the environment:

- clean production build;
- framework type, configuration, and link checks;
- output directory and ignored/generated-file expectations;
- base-path preview or equivalent route resolution;
- home, nested, deep-link, asset, anchor, not-found, and legacy-route checks;
- canonical URL, sitemap, robots, social metadata, favicon, and RSS only when needed;
- `CNAME` and custom-domain asset preservation;
- lockfile and dependency consistency;
- workflow syntax and artifact path when delivery changed.

Static checks do not prove visual, interactive, keyboard, contrast, or screen-reader behavior.

## Rendered browser verification

When browser or accessibility tooling is available:

1. serve the production output under the configured base path;
2. inspect desktop and narrow mobile layouts;
3. test navigation, search, callouts, tabs, code-copy controls, and menus;
4. traverse interactive elements by keyboard;
5. inspect focus, contrast, alternatives, zoom, touch targets, and reduced motion;
6. run an available accessibility audit and review meaningful findings manually.

If tooling is unavailable, list these checks as unverified and provide exact commands or steps. Do not describe source review as rendered QA.

## Final diff review

Check for:

- overwritten user work or unrelated formatting churn;
- duplicate package managers or conflicting lockfiles;
- unrequested or competing Pages workflows;
- hard-coded owner, repository, branch, domain, or base URL that conflicts with evidence;
- secrets, tokens, internal URLs, personal data, local absolute paths, and generated caches;
- unused theme assets, placeholder pages, broken links, and stock copy;
- documentation facts duplicated without synchronization;
- missing legacy-route mappings or lost `CNAME` behavior;
- unexplained external requests, trackers, fonts, scripts, or hosted services.
