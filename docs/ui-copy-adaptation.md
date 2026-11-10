# UI-copy adaptation, 2026-11-10

This update covers six gaps reported in a user-supplied interface-copy review:
bounded L1-transfer candidates, string-set comparison, protected spans and test
pins, deliberate-template calibration, L2 sentence structure, and observations
outside the wording scope. Canonical owners are
[humanizer](../agent-plugins/skills/humanizer/SKILL.md) for editing and
[ai-detector](../agent-plugins/skills/ai-detector/SKILL.md) for analysis.

## Source and adaptation decision

The source is private maintenance evidence supplied by the user, not an upstream
skill to execute or redistribute. The review and its binding glossary were read
locally. No private corpus, operational instructions, project paths or test
files are imported into the packages. New instructions and illustrative examples
are original project contributions under the repository license. No scripts,
network services or dependencies are added.

Under the import rubric the normalized update scores 89/100, ADD: capability
19/20, reusability 14/15, clarity 14/15, portability 15/15, safety 14/15,
maintenance 9/10, validation readiness 4/10. The validation deduction reflects
one in-sample local review without independent reader or model evaluation.
This rates the maintenance proposal, not authorship or writing quality.

## Local replay and counterevidence

The source describes approximately 175 strings. Its appendix is a heuristic
line extract, not an authoritative inventory of complete rendered messages.
The extract contains 241 source-line entries from 18 files, including multiline
fragments and comment/code residue. The local replay
read that extract with the supplied glossary and historical findings, without
editing the product or tests. Pin locations are supplied evidence, not newly
verified against live tests. No external detector was invoked or authorized.

Every F1–F15 item was reconsidered under the final reference rules:

| Case | Disposition in the local replay |
| --- | --- |
| F1, event noun | Inspect for audience friction. Prefer an explicit action over replacing it with an ambiguous pronoun. Valid noun use is not a grammatical error. |
| F2, status idiom and split alternatives | Retain the clarity concern. Keep both branches and their distinct recovery steps. Avoid adding an introductory claim or forbidden domain term. |
| F3, identity wording and form return | Report family variation and unclear reappearance. Do not equate nonappearance with loss of saved data or erase the different action in another member. |
| F4, repeated adverb | Downgrade synonym replacement to optional preference. Both repetitions can describe different actions. A sequence split is justified only if it helps the reader. |
| F5, recovery-instruction variants | Report the shorter member's omitted information. Do not add a retry instruction unless its applicability is supported. Keep named controls unchanged. |
| F6, code naming | Report operator-family drift. Keep technical naming for a distinct diagnostics audience and preserve placeholders. |
| F7, title/body scope | The body supports narrowing the title to loading a list. It does not support a claim that calls themselves are blocked. |
| F8, repeated preposition | Inspect the awkward attachment. Reject a replacement that adds a claim about what the screen displays without evidence. Final prepositions are not banned. |
| F9, progress label | An explicit conjunction can clarify the relationship. A short UI label may legitimately be a fragment. Keep the uncertain result uncertain. |
| F10, duration label | Clarifying that the value is a duration is useful if it matches the supplied field meaning and is not a protected label. |
| F11, modal expectation | Retain the ambiguity concern, reject strengthening expectation into an unconditional validation guarantee without behavior evidence. |
| F12, omitted complementizer | Adding `that` and clarifying the record referent may help this audience. The original grammar is valid. |
| F13, contractions and typography | Report optional within-family consistency. Do not impose a global contraction rule or change persistence semantics while editing register. |
| F14, equivalent indefinite pronouns | Report optional within-family consistency. Both forms are ordinary English, not AI cues. |
| F15, idioms and necessary detail | Keep, as the original item itself specifies. It is not a fifteenth defect. Preserve the training-history context and distinct action facts. |

The repeated consequence and success templates were kept. Factual contrasts
were kept. The connect-versus-ring discrepancy and an unverified visual claim
remain outside-scope observations, with no product edits. No proposed rule
authorizes changing a protected control name, fact, condition, or test merely
to improve consistency. The supplied summary's pin count is not promoted to a
verified coverage claim.

## Verification limits and reusable cases

The replay is a local editorial exercise with prior findings visible, not a
blind comparison or evidence that the new skills outperform the old ones.
Some historical suggestions were rejected or narrowed rather than requiring
all 15 to remain defects. No acceptance score, detector accuracy or user
comprehension improvement was measured.

[Activation cases](../tests/fixtures/activation_cases.json) cover large and small
UI sets, missing pin evidence, deliberate templates, local workflow analysis,
and exclusions for translation and detector-free editing. These are routing
fixtures, not executed model evaluations. Repository validation, wrapper checks
and unit tests verify packaging and existing tooling, not editorial quality.

For a future independent evaluation, use unseen UI sets with both legitimate
repetition and meaningful state differences. Check protected spans, pin-map
uncertainty, branch actions and modality before assessing stylistic benefit.
