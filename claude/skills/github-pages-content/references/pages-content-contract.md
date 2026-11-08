# GitHub Pages content contract

## Inventory before restructuring

Inventory only public, relevant material:

- README and maintained documentation;
- installation, quick-start, examples, API or CLI references;
- changelog, contribution, security, support, and license files;
- site configuration, navigation, sitemap, generated references, and existing routes;
- screenshots, diagrams, logos, and other content assets.
- supplied or already accessible GitHub Wiki pages, including known inaccessible pages as evidence gaps.

For each item record its reader, purpose, source of truth, freshness signal, current route, and disposition: keep, revise, consolidate, link, generate, or omit. Never treat repository presence alone as evidence that content is current.

Verify Wiki commands, versions, examples, and behavior against the current repository. Mark stale or conflicting material and prefer maintained canonical sources. Reading a Wiki does not authorize editing it or copying its claims unverified.

## Organize around reader tasks

Build from tasks inward rather than from the repository directory tree outward. A useful default sequence is:

1. understand the project and its verified value;
2. satisfy prerequisites;
3. complete a minimal successful task;
4. perform common tasks;
5. consult configuration or reference material;
6. troubleshoot or find support;
7. contribute, review security guidance, or inspect licensing.

Adjust this sequence to repository evidence. Omit sections without useful material.

## Define the navigation model

- **Global navigation:** a short stable set of primary destinations.
- **Local navigation:** sidebar, section index, previous/next links, or page table of contents when depth warrants it.
- **Utility navigation:** source repository, releases, contribution, support, or theme controls; keep it visually secondary.
- **Contextual navigation:** related guides and prerequisite/next-step links placed where the reader needs them.

Show the current location with a page title, active navigation state, and breadcrumbs only when hierarchy is genuinely deep. Do not hide essential desktop navigation behind an unlabeled menu. On narrow screens, collapse it into a labelled, keyboard-operable control.

## Use stable labels and routes

- Reuse project terminology that current docs and source support.
- Prefer labels that describe reader outcomes over internal team names.
- Keep labels consistent across navigation, headings, links, and search.
- Separate content hierarchy from URL mechanics, but map every changed route and important anchor to preservation, redirect, or intentional removal.
- Changing a heading can change its automatically generated anchor. Pass old/new heading and slug requirements to `github-pages-create`, which preserves the URL contract and checks actual built deep links.
- Avoid dates, versions, or implementation details in permanent routes unless they are part of the maintained public contract.

## Write repository-grounded copy

- Lead with the reader's task and the verified project behavior.
- Use specific action labels instead of vague controls such as “Submit” or “Learn more.”
- Make commands, prerequisites, expected results, and recovery steps complete.
- Keep voice consistent with repository branding; keep tone calm and direct for errors and limitations.
- Avoid invented metrics, testimonials, adoption claims, roadmaps, and generic promotional filler.
- Write headings and summaries for scanning; constrain sustained prose to a readable measure in the visual layer.

Trace material commands, versions, compatibility, API behavior, and expected example results to a current file/section or verified run. A compact source note is enough, not a ledger for every sentence. Label unresolved conflicts and assumptions.

Use an available editorial or humanizer pass only on new or substantially changed reader-facing prose when needed by the owning writing workflow. Preserve meaning, uncertainty, code, parameters, identifiers, and verified facts. Copy editing does not expand the content scope.

## Add search only when it earns its cost

Use browse navigation for small sites. For larger technical documentation, prefer a maintained build-time local index supported by the selected framework.

When search is justified:

- label what can be searched;
- support keyboard submission and result traversal;
- persist the query while refining;
- show titles, useful matching context, and relevant metadata;
- provide a constructive zero-results state with spelling or browse alternatives;
- exclude duplicate and irrelevant generated pages;
- avoid hosted search, query logging, or personalization without explicit authorization and a privacy/cost review.

## Validate content journeys

Check home and the primary successful task. Add a nested guide, reference destination, legacy route, missing-page recovery, or search-empty case only when that feature exists or changes. Mark others `not applicable` with a reason. A one-page site does not need search or nested pages to pass.

For each applicable journey check entry, orientation, next action, and recovery. Distinguish source checks from rendered observations and tested interactions. Unavailable tools leave applicable checks `not verified`.
