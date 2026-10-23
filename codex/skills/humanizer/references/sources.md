# Source decisions

Reviewed on 2026-10-23 using GitHub metadata, pinned source files, licenses, and
package inventories. Upstream descriptions are claims to inspect, not evidence
that detection scores, scientific grounding, or bypass promises work.

## Adapted sources

| Source at inspected commit | License | Selected guidance and changes |
| --- | --- | --- |
| [blader/humanizer](https://github.com/blader/humanizer/blob/8c307f367c91bd974002f10f2be2965d642c13df/SKILL.md) | MIT, copyright 2025 Siqi Chen | Adapted paragraph-level structural editing and source comparison. Removed permissions to add reactions, genre-imposed voice defaults, rigid pattern rankings, and mandatory intermediate drafts. |
| [Aboudjem/humanizer-skill](https://github.com/Aboudjem/humanizer-skill/blob/a58df065367550b6ce40ff3f648335018d8e0589/skills/humanizer/SKILL.md) | MIT, copyright 2026 Adam Boudjemaa | Adapted restraint, protection of meaningful specifics, and the distinction between a style clue and a defect. Removed preset personalities, AI scores, aggressive hedge removal, and automatic profile loading. |
| [Vladimir-Human/humanizer-ru](https://github.com/Vladimir-Human/humanizer-ru/blob/57c72f8aced31bf4c8a98e7c0eae1e3c3e452fb3/skills/humanizer-ru/SKILL.md) | MIT, copyright 2026 Vladimir | Adapted meaning anchors, proportional editing, Russian impersonal constructions, and grammatical-dash preservation. Removed automatic URL/citation cleanup and file editing inferred from a bare path. |

Complete upstream licenses are retained as
[LICENSE.blader-humanizer](../LICENSE.blader-humanizer),
[LICENSE.aboudjem-humanizer](../LICENSE.aboudjem-humanizer), and
[LICENSE.humanizer-ru](../LICENSE.humanizer-ru). Instructions and examples are
substantially rewritten. Attribution does not imply endorsement.

## Compared, not imported

| Source at inspected commit | License finding | Decision |
| --- | --- | --- |
| [harshaneel/humanize](https://github.com/harshaneel/humanize/blob/9c3dec34dc8e0ed9d26de14a869900a714da8f9e/plugins/humanize/skills/humanize/SKILL.md) | MIT | Detector-driven levers, forced punctuation changes, and statistical variation conflict with this task. Neither the rewrite nor the companion forensic auditor is bundled. Research claims were not validated. |
| [numen-tech/slopornot](https://github.com/numen-tech/slopornot/blob/71bf2ea2862817ed8d87196ddf1290ea37a439d4/skills/agentic-humanizer/SKILL.md) | MIT | Persistent profile management, voice fingerprints, MCP/CLI probing, and score loops add unwanted state and dependencies. No profiles, integrations, or tools imported. |
| [gencharitaci/humanize-skills](https://github.com/gencharitaci/humanize-skills/blob/a9f9748d067770a5be6f64b3b804f99555193964/skills/humanize-skills/SKILL.md) | CC BY 4.0, not MIT | Broad purpose modes and calibration machinery are unnecessary for the bounded edit. No source text, references, or examples imported. |
| [matsuikentaro1/humanizer_academic](https://github.com/matsuikentaro1/humanizer_academic/blob/468e67f6fd6d93bbfb257d4a685af8db89d0527b/SKILL.md) | Root file states MIT and attribution but does not reproduce the full grant | Medical-paper conventions and a preconfigured author's profile belong to that project. No source material or sentence-length checker imported. |
| [lynote-ai/humanize-text-skill](https://github.com/lynote-ai/humanize-text-skill/blob/9359e17a8d7d54263adb726f4e6c71e0b0940651/SKILL.md) | MIT | Voice targeting and local detector machinery exceed this task. Tree inspection found a root `CLAUDE.md` symlink; it was not followed or imported. No package resources imported. |
| [diaiq/claude-skill-humanizer](https://github.com/diaiq/claude-skill-humanizer/blob/fd111474c8e96ef8dbbf93538089de8b02da7b1c/SKILL.md) | MIT | The skill sends text to a public external API and advertises detector bypass. Neither the upload workflow nor its promises are imported. |
| [borghei/Claude-Skills content-humanizer](https://github.com/borghei/Claude-Skills/blob/2c12c7efaad13a70bdea6e205698a6c4f93a0682/marketing/content-humanizer/SKILL.md) | Root license is Commons Clause + MIT despite skill frontmatter saying MIT | Restrictive terms and voice injection are unsuitable for this adaptation. No text, scripts, or templates imported. |

## Local ownership and routing

The project voice inspected for compatibility keeps its active core in
`social-voice.md`, with craft, language, and task modules. Those files retain
authority and were not copied or modified. Generic humanizing decisions belong
here; the user's narrator, literary references, humour, language ceilings,
punctuation choices, and assessment procedures remain project-owned.

`humanizer` handles an existing passage's naturalness in its current language and
voice, with removing an AI-generated impression as its primary objective.
Voice preservation constrains that edit. `stop-slop` retains its detailed English phrase/structure diagnostics for
targeted pattern audits and explicit Stop Slop edits. Neither requires loading
the other or running two consecutive editing passes.

The user also requested council-based editing decisions. One bounded session
covers edit selection and critique of the exact candidate, with an unchanged
option and reuse of the same advisors. Existing project councils retain their
required stages and authority. Independent review cannot establish actual reader
perception or the author's preference without feedback.

## Intake and security result

The normalized adaptation scores **92/100, ADD** under the repository import
rubric: capability 19/20, reusability 15/15, clarity 14/15, portability 15/15,
safety 14/15, maintenance 9/10, validation readiness 6/10. Remaining limitations
are subjective editorial judgement, continuing overlap with targeted English
editing, and the need for broader real-use voice evaluations. These are skill
intake scores, not text-authorship or human-likeness scores.

Only instructions and complete licenses from the three selected sources are
adapted. Their inspected package trees contain no symlinks or submodules. No
upstream scripts, binaries, installers, hidden configuration, detector data,
credentials, private paths, dependencies, or network actions are bundled or
executed. Source links and commands remain reference material. The skill needs
only the requested text and any already applicable voice guidance.
