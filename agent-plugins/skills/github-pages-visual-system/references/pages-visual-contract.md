# GitHub Pages visual contract

## Start from repository evidence

Record the existing framework/theme, CSS entrypoints, design tokens, brand assets, favicon, screenshots, supported browsers, content types, and user changes. Reuse viable choices. A redesign must have a repository-grounded benefit, not just novelty.

## Keep the token layer small

Prefer semantic CSS custom properties or the framework's native token mechanism:

- background and elevated surface;
- primary and muted text;
- border and divider;
- action, hover, active, and focus;
- code background and code text;
- success, warning, danger, and information when those states exist;
- spacing, content width, radius, typography, and optional motion.

Components should consume semantic roles rather than one-off values. Do not create global, alias, and component token tiers unless site complexity demonstrates the need.

## Color and themes

- Derive brand accents from repository assets or documented branding.
- Check every foreground/background pairing used in rendered pages.
- Do not communicate status or link identity through color alone.
- Keep focus indicators visible across themes.
- In dark mode, remap surface and text roles deliberately; avoid raw inversion and large areas of pure black or white when they impair reading.
- Respect `prefers-color-scheme` when appropriate and preserve an accessible manual control if the chosen theme provides one.

## Typography and reading measure

- Keep body text comfortably readable at default browser zoom; do not shrink it to fit more content.
- Use a restrained hierarchy with one H1 per page and visibly distinct H2/H3 levels.
- Give code a legible monospace face and sufficient line height.
- Constrain sustained prose to roughly 45–75 characters per line, with a narrower range often preferable for long technical reading.
- Test headings, navigation labels, long commands, URLs, translated strings, and real paragraphs rather than lorem ipsum.
- Prefer system or self-hosted fonts. Adding remote fonts requires explicit operational and privacy justification.

## Spacing, grid, and hierarchy

Use a small consistent spacing scale. Keep related items closer than separate sections, and make touch targets large enough without inflating the whole layout.

Choose the simplest grid that serves the content:

- single readable column for small sites;
- navigation plus content for multi-page docs;
- optional table of contents when page length warrants it;
- responsive card grid only for genuinely parallel destinations.

Make the page title or primary proposition the first visual entry point. Keep one dominant action per view, subordinate metadata, and remove decoration that competes with the reader's task.

## Responsive behavior

Choose breakpoints where content, navigation, tables, or code stop working—not from a fixed device catalog. At each relevant width:

- reflow columns without changing reading order;
- keep essential navigation available through a labelled control;
- prevent page-level horizontal scrolling while preserving scrollable code and tables where necessary;
- scale headings without reducing body legibility;
- preserve touch targets, focus visibility, zoom, and image aspect ratios;
- avoid hover-only information or actions.

## Motion and media

Use motion only for orientation or feedback. Avoid autoplay, scroll hijacking, decorative parallax, and blocking transitions. Respect reduced-motion preferences. Give informative images meaningful alternatives, decorative images empty alternatives, and screenshots enough context to remain useful.
