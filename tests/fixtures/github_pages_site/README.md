# Crate documentation fixture

Synthetic repository material for Pages forward-testing, not a real product.
The fixture's current CLI contract is `crate scan --format json`. The minimum
supported Python version is 3.11. No adoption, uptime, or customer metrics exist.

The checked-in static site is `site/`. It uses no dependencies or compilation.
For a production preview, copy the contents of `site/` into `dist/crate/` in a
disposable directory and serve `dist/` with Python's standard HTTP server.
The Pages project base path is `/crate/`. The public deep link
`/crate/#install` must remain valid. Only the light theme is supported.

`site/tokens.css` is the accepted visual system. Reuse its cream and terracotta
palette, locally available typography with system fallback, shared spacing,
navigation and reference styles. New pages use that file. Remote fonts and
services are outside scope. The navigation has two equal lookup destinations.

`wiki/Setup.md` is available historical material. Current compatibility and
command facts above supersede its old instructions. Wiki edits are not requested.
