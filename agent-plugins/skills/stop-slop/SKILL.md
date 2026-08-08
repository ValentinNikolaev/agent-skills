---
name: stop-slop
description: Review or edit primarily English prose to remove formulaic AI-sounding phrases and structures while preserving meaning, evidence, qualifications, voice, formatting, and protected text. Use only when the user explicitly asks to humanize, de-slop, remove AI tells, or apply Stop Slop to pasted text or named files. Do not invoke for routine drafting, code, creative voice, house-style work, or legal, academic, and technical precision edits unless the user explicitly requests this treatment.
---

# Stop Slop

Remove formulaic writing without replacing the author's meaning or voice with another formula.

## Preserve meaning before style

Treat semantic integrity as the highest-priority rule.

- Keep claims, numbers, names, dates, causal relationships, uncertainty, modality, and scope unchanged.
- Never add achievements, examples, evidence, metrics, credentials, or experience that the source does not contain.
- Preserve citations and source attribution.
- Do not strengthen `may`, `some`, or `most` into universal claims.
- Do not remove legally, technically, or academically necessary qualifications.
- When a stronger rewrite needs missing facts, use an explicit placeholder or ask for them.

If a style heuristic conflicts with accuracy, genre, author intent, or readability, ignore the heuristic.

## Protect immutable spans

Do not alter these unless the user specifically includes them in scope:

- direct quotations and interview excerpts;
- code, commands, formulas, data, and configuration;
- citations, footnotes, URLs, and reference labels;
- product names, legal terms, defined terms, and proper nouns;
- placeholders, template variables, and required application fields.

Preserve Markdown, document structure, links, and other formatting outside the requested edit.

## Choose the operation

- **Review**: Identify formulaic patterns and explain targeted improvements. Do not rewrite or edit files.
- **Rewrite**: Return revised pasted prose while preserving its facts and structure unless the user requests broader restructuring.
- **File edit**: Edit only explicitly named files after the user asks for file changes. Inspect the diff and avoid unrelated formatting churn.

When the operation is unclear, prefer review for named files and rewrite for pasted text. Do not infer permission to edit a file from a request to review it.

## Choose the strength

- **Light**: Remove obvious filler and repetition while preserving nearly all phrasing.
- **Standard**: Remove recurring AI tells and improve rhythm without flattening genre or voice. Use by default after explicit invocation.
- **Strict**: Apply stronger compression for marketing, opinion, or outreach prose. Use only when the user asks for a strict or punchy rewrite.

For legal, academic, technical, policy, accessibility, or compliance prose, remain conservative even in strict mode.

## Apply genre-aware heuristics

Read [references/phrases.md](references/phrases.md) when phrase-level patterns are relevant. Read [references/structures.md](references/structures.md) when rhythm or organization is the problem. Read [references/examples.md](references/examples.md) only when an example helps resolve ambiguity.

Treat every listed pattern as a diagnostic signal, not an automatic ban.

1. Cut throat-clearing that delays the point.
2. Replace vague importance claims with the specific consequence already supported by the source.
3. Reduce repeated binary pivots, dramatic fragments, rhetorical setups, and meta-commentary when they feel mechanical.
4. Prefer active voice when the actor matters and is known; keep passive voice when the actor is unknown, irrelevant, deliberately withheld, or genre-appropriate.
5. Name human actors only when the source supports them. Do not invent an actor to avoid inanimate wording.
6. Vary rhythm according to the genre. Keep useful lists, questions, short sentences, and punctuation.
7. Preserve meaningful adverbs, transitions, emphasis, and em dashes when they carry precision or voice.
8. Avoid mirroring job titles, team names, document headings, or prompts as empty openers; retain them when the reader needs the context.
9. Replace generic claims of fit or impact with verified evidence already present, not fabricated specifics.

## Respect language and voice

The bundled phrase and syntax references target English. For other languages, apply only the general goals of directness, specificity, semantic preservation, and natural rhythm unless the user supplies language-specific guidance.

Preserve deliberate dialect, humor, rhetorical style, brand voice, and memorable phrasing. Do not remove a construction merely because it could appear in AI writing.

## Validate the result

Before delivery:

1. Compare every factual claim, number, name, date, qualifier, and citation with the source.
2. Confirm protected spans and formatting remain intact.
3. Check that no placeholder became a fact and no example was invented.
4. Read the result for genre fit, coherent rhythm, and preserved author voice.
5. Remove only patterns that materially improved the text.

For review mode, return findings with examples and suggested revisions. For rewrite mode, return the revised prose and briefly disclose any material structural change. For file-edit mode, summarize edited files and verification.

## License

See [LICENSE](LICENSE).
