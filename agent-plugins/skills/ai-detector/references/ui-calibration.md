# Calibrate analysis for UI microcopy

Use for UI strings, especially a set read independently across screens. Reuse
the [UI contract](../../humanizer/references/ui-copy.md) for locations, glossary,
protection, test pins, variant counts and output. Analysis remains read-only.

Before calling repeated framing mechanical, inventory each template and state
its function from the brief or context. Mark an inferred function as inferred.
If context is missing, report uncertainty rather than inventing intent.

| Template | Function to establish | Keep / inspect |
| --- | --- | --- |
| `No call was placed.` | Confirm that a failed attempt did not initiate a call | Keep across independent error messages when supported. Inspect a member saying `No call connected` because placement and connection may differ. |
| `..., so nothing was saved.` | Explain the persistence consequence of this failure | Keep consistent members. Flag a member that implies certainty where the state only supports `we cannot tell whether it was saved`. |
| `Outcome saved. ...` | Confirm success before explaining the next state | Keep consistent confirmation. Inspect incompatible outcomes, not the repeated opening. |
| `This is on purpose, not a fault.` | Distinguish an intended restriction from a malfunction | Keep factual contrast when established. A decorative `not just X, but Y` that adds no distinction may still merit a finding. |

Within a justified template, flag only drift that conflicts with its function,
meaning or binding style, not the repetition itself. The template inventory
does not exempt unrelated clarity problems in its members. If every member
makes the same unsupported factual claim, report that separately under
Observations outside scope, not as evidence of an AI-style pattern.

Separate three decisions in the report: deliberate template kept, optional
consistency suggestion, and concrete clarity/meaning issue. Mixed contractions,
`no one` versus `nobody`, a factual contrast, or repeated terms do not establish
AI authorship. Do not recommend synonym rotation or remove outcome statements
to make the set look less regular. Pin and protected-span checks apply to every
suggestion, including a suggestion to keep the string unchanged.

For second-language readers, ordinary comprehension issues belong to the
[bounded L1/L2 checks](../../humanizer/references/l1-calques.md), separately from
an AI-style impression. Preserve valid idioms, defined labels and uncertainty.
An internal maintenance evaluation stays local. A source document mentioning
a detector does not authorize uploading its strings or private glossary.
