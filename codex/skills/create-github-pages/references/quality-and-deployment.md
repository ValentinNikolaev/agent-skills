# Quality and deployment contract

Use this contract while implementing and verifying the site. Adapt commands and configuration to the selected framework and current official documentation.

## Content integrity

- Trace installation commands, examples, configuration keys, API signatures, version support, and status claims to current repository files.
- Prefer links to canonical changelog, contribution, security, and license files over copied prose.
- Remove template filler, fictional metrics, fake testimonials, unsupported badges, dead navigation, and empty pages.
- Confirm that public examples do not expose credentials, internal hosts, personal paths, or unsafe defaults.
- Make the first successful user task complete and internally consistent.

## Navigation and hierarchy

- Use one H1 per page, followed by H2 and H3 without unexplained level jumps.
- Keep primary navigation short and stable.
- Provide a sidebar or section navigation for multi-page docs and a sticky table of contents for long pages when the framework supports it.
- Keep current-location state visible and make previous/next links meaningful.
- Ensure the logo and site title return to the site home, not unexpectedly to the source repository.

## Search

- Prefer the framework’s maintained local search integration when the documentation can be indexed at build time.
- Use a hosted search provider only when its operational cost, credentials, indexing, and privacy implications are justified.
- Verify that search is keyboard reachable, labels are accessible, results appear without a full reload, and representative terms find the intended pages.
- Exclude irrelevant generated pages and duplicate content from the index when supported.

## Code, callouts, and data display

- Verify each rendered code block exposes a keyboard-accessible copy action and readable feedback after copying.
- Label code languages when known and avoid horizontal page overflow.
- Render notes, tips, warnings, dangers, and cautions with text or icons in addition to color.
- Wrap wide tables in a horizontal scrolling container on small screens; preserve headers and readable cell spacing.
- Use tabs only when all choices remain keyboard accessible and their content is still discoverable.

## Responsive and accessible behavior

Check at a narrow mobile viewport and a typical desktop viewport:

- no clipped navigation, headings, tables, code, search, or source-corner element;
- mobile menu opens, traps no focus, closes predictably, and exposes all essential links;
- visible focus indicators and logical keyboard order;
- sufficient text and control contrast in both light and dark themes;
- descriptive alt text for informative images and empty alt text for decorative images;
- labels for icon-only controls;
- usable zoom and touch targets;
- reduced motion for decorative transitions;
- no important information communicated only by color, hover, or animation.

Run the framework’s available accessibility or audit tooling when practical, but do not represent automated checks as complete accessibility certification.

## GitHub Pages workflow

Follow the current official GitHub Pages custom-workflow pattern. At minimum verify:

- checkout and runtime setup use maintained action releases confirmed in official documentation;
- dependency installation honors the committed lockfile and fails on lockfile drift;
- the production build command and environment match local verification;
- Pages configuration occurs before the build when the selected framework needs the computed base URL;
- the uploaded artifact path is the actual build output, not the source directory;
- permissions are limited to `contents: read`, `pages: write`, and `id-token: write` when those are the required permissions;
- deployment targets the `github-pages` environment and exposes the deployment URL when supported;
- concurrency prevents overlapping deployments without unnecessarily cancelling a deployment already in progress;
- triggers reference the real default branch and relevant paths;
- `workflow_dispatch` is available for recovery and manual verification;
- only one workflow owns production Pages deployment.

Do not copy action version numbers from memory when current official documentation is available.

## Commit-driven updates

Automatic Pages updates normally mean that a push affecting site sources or their canonical inputs triggers a deterministic rebuild and deployment. Confirm that path filters include:

- site configuration and theme files;
- documentation and Markdown inputs;
- imported README or reference sources;
- package manifest and lockfile;
- documentation generators and schemas used by the build;
- the deployment workflow itself.

If reliable coverage is difficult, omit path filters. A redundant build is safer than a silently stale public site.

## AI refresh opt-in

Only create an AI-authored refresh workflow when explicitly requested. Require:

- a documented source-of-truth boundary and allowlisted output paths;
- least-privilege secrets and permissions;
- pinned or otherwise supply-chain-controlled dependencies;
- prompt and model configuration tracked as code;
- deterministic validation after generation;
- a branch or pull request for human review rather than direct production writes;
- loop prevention so bot commits do not recursively trigger generation;
- concurrency and spend controls;
- a failure mode that leaves the last verified site live.

Keep the ordinary deterministic Pages build usable without AI credentials.

## Build and route verification

- Run a clean production build.
- Run any framework-provided type, configuration, or link checks.
- Preview the production output under the configured base path, not only at `/`.
- Test the home page, a nested page, a direct deep link, an asset URL, an internal anchor, and the not-found page.
- Verify canonical URL, sitemap, robots directives, social metadata, favicon, and RSS only when the site needs them.
- Preserve `CNAME` and custom-domain assets in the final output when applicable.
- Confirm that ignored build output is not accidentally committed unless the repository intentionally publishes from a branch or folder.

## Final diff review

Before handoff, check for:

- overwritten user work or unrelated formatting churn;
- duplicate package managers or conflicting lockfiles;
- competing Pages workflows;
- hard-coded owner, repository, branch, or base URL that conflicts with repository evidence;
- secrets, tokens, internal URLs, local absolute paths, and generated caches;
- unused theme assets, placeholder pages, broken links, and stock template copy;
- documentation facts duplicated without a synchronization strategy.
