# Rendered GitHub Pages audit

## Preconditions and evidence

Serve the production output under the expected project or custom-domain base path. Record unavailable tools and inaccessible routes. Use repository files as the authority for branding, supported content, and intended behavior; do not invent a design specification.

## Reader journey and information architecture

- The site's purpose and primary next action are apparent on entry.
- Installation or first-success instructions include prerequisites, commands, expected result, and recovery.
- Global and local navigation use consistent labels and expose the current location.
- Important destinations are reachable without relying on search.
- Links, breadcrumbs, previous/next controls, and source/edit links go where their labels predict.
- Legacy deep links, anchors, assets, and not-found behavior work under the production base path.

## Content and density

- Each page has one clear primary task and removes unrelated filler.
- Headings, summaries, lists, and callouts support scanning.
- Primary information is not buried in tooltips, collapsed regions, or low-contrast metadata.
- Commands, names, versions, and claims agree with repository evidence.
- Empty, missing, and zero-results states explain what happened and offer a useful next action.

## Visual hierarchy and brand

- The page title or primary proposition is the first meaningful visual entry point.
- Heading levels, body text, metadata, links, and primary actions have distinct roles.
- Spacing groups related content and separates sections consistently.
- Colors, type, radii, icons, logos, and imagery follow repository tokens or documented branding when available.
- Hard-coded exceptions are justified rather than accidental drift.

## Responsive layout

At representative desktop and narrow mobile widths verify:

- navigation remains available and does not obscure content;
- reading order survives column reflow;
- tables, code, long URLs, headings, media, and controls do not clip;
- page-level horizontal scrolling is absent;
- touch targets and spacing remain usable;
- zoom and increased text size do not hide information or actions;
- hover is not the only way to discover or operate a control.

## Accessibility and interaction

- Keyboard order is logical and focus is visible in every theme.
- Skip links, landmarks, headings, link names, button names, and form labels are meaningful.
- Informative images have useful alternatives; decorative images are ignored appropriately.
- Text and component contrast are checked for the actual rendered pairings.
- Status, warnings, links, and callouts do not rely on color alone.
- Mobile menus, search, tabs, copy buttons, and theme controls expose state and work without a pointer.
- Motion respects reduced-motion preferences and does not block reading or navigation.
- Focus is not trapped or lost when menus, dialogs, or route transitions occur.

## Search and technical content

When present:

- search is labelled, keyboard reachable, and returns representative repository terms;
- results show enough matching context to choose a destination;
- zero results provide correction or browse alternatives;
- code languages are identified when known;
- copy controls announce success and remain keyboard operable;
- code and tables scroll locally without forcing the entire page to overflow.

## Severity

- **Critical:** blocks access to the site or a primary task for an affected audience.
- **Major:** causes substantial difficulty, broken navigation, or loss of important content.
- **Minor:** creates friction or inconsistency with a practical workaround.
- **Enhancement:** improves quality without repairing a demonstrated failure.

Automated findings require manual confirmation. Missing tooling belongs in audit limitations, not silently in a passing verdict.
