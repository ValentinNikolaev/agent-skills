# GitHub Pages content contract

## Inventory before restructuring

Inventory only public, relevant material:

- README and maintained documentation;
- installation, quick-start, examples, API or CLI references;
- changelog, contribution, security, support, and license files;
- site configuration, navigation, sitemap, generated references, and existing routes;
- screenshots, diagrams, logos, and other content assets.

For each item record its reader, purpose, source of truth, freshness signal, current route, and disposition: keep, revise, consolidate, link, generate, or omit. Never treat repository presence alone as evidence that content is current.

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
- Avoid dates, versions, or implementation details in permanent routes unless they are part of the maintained public contract.

## Write repository-grounded copy

- Lead with the reader's task and the verified project behavior.
- Use specific action labels instead of vague controls such as “Submit” or “Learn more.”
- Make commands, prerequisites, expected results, and recovery steps complete.
- Keep voice consistent with repository branding; keep tone calm and direct for errors and limitations.
- Avoid invented metrics, testimonials, adoption claims, roadmaps, and generic promotional filler.
- Write headings and summaries for scanning; constrain sustained prose to a readable measure in the visual layer.

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

Test at least the home page, minimal successful task, one nested guide, one reference destination, a changed legacy route, and a missing/search-empty case. Check that each journey has clear entry, orientation, next action, and recovery.
