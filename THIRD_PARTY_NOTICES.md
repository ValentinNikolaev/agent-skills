# Third-party notices

Except where noted below, original content in this repository is distributed
under the [MIT License](LICENSE). Third-party material remains subject to its
respective terms; the repository license does not relicense that material.

## PHP, Python, and TypeScript review references

The `code-review` references `review-php.md` and `review-python.md`, along with
selected type-safety, async, module, resource-management, and testing checks in
`review-typescript.md`, adapt and substantially rewrite selected topics from
[`awesome-skills/code-review-skill` at commit
`4850184dfd7765ea7b3c5c4e9b6cf8e0815ee7cb`](https://github.com/awesome-skills/code-review-skill/tree/4850184dfd7765ea7b3c5c4e9b6cf8e0815ee7cb),
specifically `reference/php.md`, `reference/python.md`, and
`reference/typescript.md`. The upstream work is distributed under MIT,
copyright 2025 awesome-skills. Its license is retained as
`agent-plugins/skills/code-review/LICENSE.awesome-skills` and in both generated
copies. The adaptation omits the upstream general reviewer, scripts, mandatory
tools, formatter changes, coverage thresholds, and project-wide tool runs.

## Go workflows and conditional references

The Go checks in `code-review`, the `go-security-audit` and `go-benchmark`
skills, and selected conditional Go guidance in `review-arch`,
`code-simplification`, `debugging-and-error-recovery`, `vet-dependency`, and
`console-ux-design` adapt and substantially rewrite selected workflows and
references from Samuel Berthe's
[`samber/cc-skills-golang` at commit
`8e899e20ff0cd4dc524af3993e4c62d8ee8c5717`](https://github.com/samber/cc-skills-golang/tree/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717).
The selected topics include security, benchmarks/performance, concurrency,
context, safety, errors, testing, database access, observability, refactoring,
troubleshooting, dependencies, design patterns, and command-line interfaces.
The upstream MIT license is retained as `LICENSE.samber-cc-skills-golang` in
each affected canonical package and both generated copies. The adaptations
omit automatic delegation, installations, fixes during audit, mandatory
numeric scoring, production access, and external workflow configuration.

The Go checks in `code-review`, the Go specification reference in
`review-spec`, and selected conditional guidance in `api-and-interface-design`,
`deprecation-and-migration`, and `console-ux-design` also adapt and substantially
rewrite Steve Francia's
[`spf13/go-skills` at commit
`9ac6eca43161163bb21621a520a57df50d5ad464`](https://github.com/spf13/go-skills/tree/9ac6eca43161163bb21621a520a57df50d5ad464),
including its Go, specification review, Cobra/Viper, and release-compatibility
guidance. The upstream MIT license is retained as `LICENSE.spf13-go-skills` in
each affected canonical package and generated copies. The adaptations replace
global project-layout preferences and tool mandates with version- and
repository-dependent checks. No material from the unlicensed Teetsh source is
bundled. Attribution does not imply endorsement by upstream maintainers.

## PHP modernization

The `php-modernization` skill body and its
`references/compatibility-and-tools.md` adapt and substantially rewrite
Netresearch DTT GmbH's
[`php-modernization-skill` at commit
`8df68546e8d9fa00e4530e9c26e73adcc3322834`](https://github.com/netresearch/php-modernization-skill/tree/8df68546e8d9fa00e4530e9c26e73adcc3322834),
including its skill definition and selected migration, typing, immutability,
and tooling references. Upstream content is licensed under
[CC-BY-SA-4.0](https://creativecommons.org/licenses/by-sa/4.0/), copyright
2025-2026 Netresearch DTT GmbH. These adapted documents remain under
CC-BY-SA-4.0 rather than the root MIT license. The upstream license notice and
an adaptation notice are retained as `LICENSE.netresearch-content` and
`NOTICE.netresearch` in the canonical skill and generated copies. Changes
include scoped preview/apply, version-dependent framework checks, explicit
execution side effects, and incomplete-verification states. Original UI
metadata remains under the repository MIT license. No upstream scripts,
Composer plugin, installer, or workflows are bundled. Attribution does not
imply endorsement.

## Stop Slop

The `stop-slop` skill is adapted from
[`hardikpandya/stop-slop`](https://github.com/hardikpandya/stop-slop), by Hardik
Pandya. The upstream work is distributed under the MIT License. Its license
text is retained in `agent-plugins/skills/stop-slop/LICENSE` and in generated
distribution copies.

## LLM Council

The `council` skill is adapted from
[`aiwithremy/claude-skills-llm-council`](https://github.com/aiwithremy/claude-skills-llm-council),
built by Ole Lehmann, and from Andrej Karpathy's
[`llm-council`](https://github.com/karpathy/llm-council) methodology.

The imported upstream Council repository did not publish a license file when
this notice was reviewed on 2026-08-08. This notice records provenance and does
not assert redistribution rights beyond those granted by the respective
rights holders.

## Write Cover Letter

The `write-cover-letter` skill adapts and paraphrases the job-analysis,
evidence-mapping, and narrative framework from
[My Guide To Writing A Killer Cover Letter](https://www.reddit.com/r/datascience/comments/tag8l5/my_guide_to_writing_a_killer_cover_letter/).
The source guide and screenshots are not bundled. This notice records
methodological provenance and does not assert redistribution rights in the
source material.

## Code Review

The `code-review` skill adapts and paraphrases review-ordering, structural
quality, verification-story, dependency-review, and conditional checklist
ideas from Addy Osmani's
[`agent-skills`](https://github.com/addyosmani/agent-skills/tree/7676817c12a1317454ae3898a0c5c1eacf5dd3d5),
including `skills/code-review-and-quality/SKILL.md` and the repository-level
references. The upstream work is distributed under the MIT License. Its
license text is retained as the scoped third-party file
`agent-plugins/skills/code-review/LICENSE.addyosmani-agent-skills` and in
generated distribution copies. Original repository-authored portions remain
covered by the repository's root [MIT License](LICENSE).

The `debugging-and-error-recovery`, `planning-and-task-breakdown`,
`test-driven-development`, `write-spec`, `deprecation-and-migration`,
`code-simplification`, `api-and-interface-design`, and `write-adr` skills adapt
the corresponding workflows in Addy Osmani's [`agent-skills` at commit
`2686b620fc1fed2e8f60c704839c766b8594c6b6`](https://github.com/addyosmani/agent-skills/tree/2686b620fc1fed2e8f60c704839c766b8594c6b6).
`write-spec` adapts `spec-driven-development`; `write-adr` adapts the ADR part
of `documentation-and-adrs`. These are condensed, platform-neutral rewrites
with repository-specific routing and verification boundaries, not verbatim
copies. The upstream MIT license is retained in each of the eight canonical
skill packages and their generated distribution copies.

## Serghei Iakovlev's .agents

The `review-spec`, `review-arch`, `verify-impl`, `prove-checks`, `monitor-ci`,
and `vet-dependency` skills adapt the workflows in
[sergeyklay/.agents](https://github.com/sergeyklay/.agents/tree/d33b2b78562c7a488415bcd99ced8d7de027784a/.agents/skills),
by Serghei Iakovlev. The `code-review` and `fix-pr` skills also incorporate
selected verification, Go and TypeScript testing, and feedback-triage ideas
from that source. The upstream work is distributed under the Apache License,
Version 2.0. Its license and NOTICE are retained with the six new canonical
skills, `code-review`, and `fix-pr`, and in their generated distribution copies. The
adaptations are changed from the source and omit its project-specific paths,
mandatory file outputs, and external-service requirements.

## Designer Skills

The `github-pages-content-architecture`, `github-pages-visual-system`, and
`audit-github-pages-ux` skills, along with `console-ux-design`, adapt and
substantially rewrite selected design, content-architecture, accessibility,
responsive-layout, visual-critique, information-architecture, interaction,
writing, and validation guidance from MC Dean's
[`Owl-Listener/designer-skills`](https://github.com/Owl-Listener/designer-skills/tree/20e34c4a587e5eb09fcdf8351fa97b3ad761b31e).
The console skill translates those selected principles into command-line-native
contracts and removes web-, mobile-, and graphical-interface implementation
guidance.
The upstream work is distributed under the MIT License. Its license text is
retained as `LICENSE.designer-skills` in each canonical skill and generated
distribution copy.

## Garden Skills

The `github-pages-visual-system` skill adapts and substantially rewrites selected
design-calibration, existing-UI redesign, direction-exploration, composition
critique, and contextual failure-pattern guidance from ConardLi's
[`garden-skills` web-design-engineer at commit
`7a6d5a72e4f44bb4cc0c23c01b3d97205c723b68`](https://github.com/ConardLi/garden-skills/tree/7a6d5a72e4f44bb4cc0c23c01b3d97205c723b68/skills/web-design-engineer).
The adaptation uses a small Pages-specific direction library rather than
copying the upstream brand recipes, code templates, CDN dependencies, or
mandatory confirmation checkpoints. Adjacent Pages skills link to these
canonical references; they do not duplicate the adapted material.
The upstream work is distributed under the MIT License. Its license text is
retained as `LICENSE.garden-skills` in the canonical visual-system package and
its generated distribution copies. Brand references in the upstream material
are not treated as official design specifications or rights to brand assets.
