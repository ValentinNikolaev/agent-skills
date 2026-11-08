# Framework selection

Choose from repository evidence, existing tooling, content scale, and maintenance needs. Do not select a framework solely because it is fashionable.

Before selecting any named option, verify its current maintained status, supported runtime, GitHub Pages guidance, and relevant feature documentation from official sources. Treat this matrix as a decision aid, not evidence that a dependency is still suitable.

## Decision order

1. Keep an existing healthy site stack when it can satisfy the request without disproportionate work.
2. Match the repository ecosystem when two options are otherwise equivalent.
3. Choose a modern documentation SSG for software, tools, APIs, or multi-page knowledge bases.
4. Choose a lightweight static or Jekyll implementation for a small, stable site where search and deep navigation are unnecessary.
5. Use the framework the user explicitly requests unless it conflicts with a hard repository constraint; explain the conflict before substituting another option.

## Selection matrix

| Approach | Prefer when | Avoid when | Expected strengths |
| --- | --- | --- | --- |
| VitePress | The project is in the JavaScript/TypeScript or Vue ecosystem, Markdown is central, and the site needs fast docs navigation with modest configuration. | The project needs complex versioned docs, a built-in blog-first model, or a non-Node toolchain constraint. | Fast navigation, clean documentation defaults, local search options, theme customization, code-focused Markdown. |
| Docusaurus | The project needs documentation versioning, localization, a blog, or a broad plugin ecosystem. | The site is tiny or the additional React/configuration surface is not justified. | Mature docs information architecture, versioning, search integrations, reusable React components. |
| Starlight | Accessibility, content performance, framework-agnostic Markdown/MDX, and rich documentation components are priorities. | The repository cannot reasonably adopt the Astro/Node toolchain or depends on a framework-specific feature elsewhere. | Strong accessible defaults, responsive documentation layout, cards, tabs, asides, and flexible content collections. |
| Jekyll with a classless stylesheet | The repository needs one or a few durable Markdown pages, minimal JavaScript, and native GitHub Pages compatibility is valuable. | The user requires rich instant search, complex navigation, or highly interactive components. | Small dependency surface, Markdown-first authoring, simple maintenance. |
| Plain HTML/CSS with a classless stylesheet | A single landing page is sufficient and no Markdown build pipeline is needed. | Documentation must remain Markdown-native or needs automatic navigation/search. | Lowest build complexity and full control over a small site. |

Water.css, Pico CSS, Sakura, and similar stylesheets can provide polished native-element defaults. Load them through the actual HTML template, Jekyll layout, or framework head configuration. Do not claim that an arbitrary stylesheet line at the top of a Markdown file will work without a renderer that preserves and places it correctly.

Before adding a stylesheet, framework, plugin, or script:

- verify its license and provenance;
- prefer a maintained package pinned through the repository lockfile or a reviewed self-hosted asset;
- document unavoidable external requests and their privacy implications;
- use integrity controls when loading immutable third-party assets from a remote origin;
- inspect install scripts and avoid an additional package manager.

## Content scale heuristic

- One page, fewer than roughly six sections: prefer lightweight static or Jekyll unless the repository already uses an SSG.
- Several task guides plus reference material: prefer VitePress or Starlight.
- Versioned product documentation, localization, or integrated blog: prefer Docusaurus.
- Existing working docs framework: improve it in place unless migration has a measurable benefit and the user accepts the migration cost.

Treat these as heuristics, not fixed thresholds.

## Project-type adaptations

### Library, SDK, CLI, or API

Prioritize installation, compatibility, minimal example, common tasks, configuration, reference, troubleshooting, and contribution. Pull API and CLI facts from source, schemas, tests, or existing generated references.

### Application or service

Prioritize the user problem, screenshots, deployment or usage path, configuration, security/privacy facts, architecture only when useful, and support links.

### Documentation or wiki repository

Prioritize findability: structured sidebar, global search, previous/next navigation, stable URLs, edit links, callouts, and link validation.

### Data, research, or educational repository

Prioritize methodology, provenance, reproducibility, environment setup, dataset or license constraints, results with evidence, and citation guidance.

### Small personal or showcase project

Prioritize a concise narrative, project visuals, verified capabilities, demo/source links, and one clear call to action. Avoid manufacturing documentation depth.

## Base path decision

Distinguish these cases before configuring asset and route URLs:

- User or organization site: typically served at the domain root from a specially named repository.
- Project site: typically served beneath `/<repository-name>/`; configure the SSG base accordingly.
- Custom domain: preserve `CNAME` and follow the framework’s current custom-domain guidance; root-path assumptions may differ.

Derive owner and repository name from the Git remote when available. Treat renamed repositories, forks, preview deployments, and missing remotes as uncertainty to surface rather than guess away.
