# UI copy and sets of strings

Use this contract for interface copy or a brief naming second-language readers.
It extends the editing contract, without authorizing product, code, or test changes.
For other prose, use only the relevant audience and protection checks.

## Inputs and protection

Reuse available inputs before asking for missing information:

| Input | Record |
| --- | --- |
| Exact source | Version or diff, file:line or stable string ID, full rendered text, screen and state. |
| Reader and operation | Language, audience, review versus edit, and permitted file scope. |
| Glossary | Path/version of binding terms and style rules, including named controls. |
| Protected spans | Exact labels, placeholders, markup, quoted service messages, and other immutable text. |
| Pin map | String ID/location to test or snapshot file:line, assertion type, and search scope. |

A test pin is a dependency, not automatically a protected label. A protected
span remains unchanged unless the user explicitly includes it in the edit.
For a permitted copy change, report each known test dependency. Update tests
only when authorized, preserving their behavioral assertions rather than
weakening them to accept any wording. If tests are outside scope, leave the
change as a proposal with that dependency unresolved.

Build or verify a pin map with bounded repository searches when sources are
available. Search exact text, stable fragments, string keys and snapshots as
appropriate. Record `unknown` for an unverified map or incomplete search,
`none found in <scope>` only after searching. Never equate no search match with
proof that no test depends on a string. Keep supplied map locations distinct
from locations verified against the current version.

## Set mode

Use for 20+ UI strings or an explicit request to compare a set of any size.

1. Freeze the set and inventory its source locations. Reconstruct multiline
   strings and distinguish visible text, accessibility text, code and comments.
   If only a heuristic extract is available, disclose its omissions and count
   entries separately from complete rendered strings. Do not invent a total.
2. Group by sentence frame **and function/state/audience**, not shared words
   alone. Inventory intended templates and state the function each serves.
3. Count variants within each family. Cover error-code naming, contractions,
   `no one`/`nobody`, and recovery instructions expressed in different ways.
   Report the majority form and file:line evidence, or `tie`/`insufficient data`.
   Glossary rules and semantic distinctions outrank frequency. A majority is
   descriptive evidence, never permission to normalize the whole set.
4. Explain whether each difference changes a reader's interpretation, violates
   the binding guide, or is only an optional consistency choice. Preserve
   emphasis, deliberate full forms, distinct actions and technical vocabulary
   for a different audience. Mixed contractions alone are not an error.
5. Propose located changes with pins and protection status. Never silently
   rewrite the set. In authorized edit mode, apply only justified in-scope
   changes and check each against the original facts and protected spans.

Use a drift table, for example:

| Frame/function | Variants and counts | Majority and locations | Decision |
| --- | --- | --- | --- |
| Failed save, operator screen | `code {status}`: 3, `HTTP {status}`: 1 | `code`: ui/save.ts:10, :20, :30 | Propose the glossary term at ui/save.ts:40. Keep `HTTP` on the separate diagnostics screen. |

The numbers above are illustrative, not counts from a user's input. Do not
flatten `was not saved` and `cannot tell whether it was saved` into one frame.
Do not replace repeated `again` with synonyms merely to create variety.
Keep deliberate UI templates under the
[detector's microcopy calibration](../../ai-detector/references/ui-calibration.md).

## Findings and observations

For review output, use one row per affected string/location:

| Location or ID | Current span and reader effect | Replacement or keep | Pin location/status | Protected yes/no/unknown |
| --- | --- | --- | --- | --- |
| ui/save.ts:40 | Naming differs within the same operator message family | `(code {status})` | tests/save.test.ts:18, supplied map | yes: `{status}`, retained |

List the protected spans, not just the flag. `Yes` means the string contains
protected text, not that the entire string is uneditable. If a faithful
replacement cannot be established, write `no replacement pending evidence`.
Preserve named controls exactly, including case, punctuation and ellipses.

Use **Observations outside scope** for factual contradictions, uncertain
behavior, unverified visual claims, or product questions found during a wording
pass. Give location, observed discrepancy, evidence needed and `not edited`.
For example, `will connect` and `will ring` may describe different events.
Do not choose a verb without behavioral evidence. A clearer title can name a
list when the body explicitly says only list loading failed, but cannot assert
that calling itself failed.

Keep observations separate from wording findings and keep decisions. Include
this section only when relevant and the requested output permits commentary.
For strict text-only output, return only faithful usable text, leave uncertain
claims unchanged, and retain observations in an already-authorized report or
handoff if one exists. Do not append a report or create a side file just to
bypass the output contract. Ask only if the ambiguity prevents the requested
faithful edit.
