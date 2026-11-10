# L1-transfer candidates and L2 structure

Load only for UI microcopy or a brief naming second-language readers. These
English examples are prompts to inspect comprehension in context. They are not
proof of first-language transfer, a universal blacklist, or rules to translate
into other languages. Many are ordinary idioms or valid English noun uses.
The binding glossary and observed UI behavior decide whether a change helps.

## Bounded wording candidates

| Candidate | Possible plain alternative | Keep when / boundary |
| --- | --- | --- |
| `A second press would be refused` | `Pressing Call again would be refused` when `Call` is the exact control name | `press` is a valid noun. Keep it for input-event documentation or a reader who knows the term. Do not replace it with a vague `it`. |
| `the message about your last press` | `the message about the last time you pressed Call` | Keep a defined event term. Do not say a message appeared *after* the press unless timing is established. |
| `where the customer stands now` | `the customer's current status` when status is the actual field/concept | Keep `stands` for stance or position. A replacement must not invent a status field. |
| `this form may not come back` | `this form may not appear again` | Keep `come back to this page` when it clearly instructs navigation. Do not replace nonappearance with loss of saved data. |
| `hold your pointer over the icon` | `move your pointer over the icon` if hovering alone triggers the result | Keep `hold` when a dwell interval matters or the glossary chooses it for this audience. Do not substitute `click` or assume a touch interface supports hover. |
| `the request went out` | `the request was sent` if transmission is known | Keep literal movement or a familiar idiom in narrative. `Sent` does not mean received or accepted. |
| `pick up` | `answer the call` when answering is the action | Keep a physical pickup instruction, a protected label, or an audience's established term. Do not infer a customer answered from a connection event. |

## L2 structure

Check how the reader identifies the actor, action, condition and referent, not
a reading grade or sentence-length target. Suggest a change only for concrete
friction, and compare the whole sentence after the change.

- **Split alternatives:** In `Either A. Do X. Or B. Do Y.`, make each action's
  branch explicit. For example, `Either A, in which case do X, or B, in which
  case do Y.` Preserve uncertainty about which branch occurred. Do not turn
  alternatives into sequential steps. Keep separate sentences or bullets when
  their branches are already clearly labelled.
- **Omitted complementizer:** `Check it's the right customer` can become
  `Check that this is the right customer` when the matched record is the
  referent. Omitted `that` is grammatical. Keep `Check the number` or an
  unambiguous `Check that it is correct` without adding redundant scaffolding.
- **Distant pronoun:** In `Nothing is lost if you leave it`, establish whether
  `it` means the page, form or call before naming it. Repeat a known noun when
  helpful. Keep nearby unambiguous pronouns, and do not guess an unclear object.
- **Expectation and blame:** `The form should have sent your reason` can
  obscure whether this is an expectation, obligation, or confirmed failure.
  `The form was expected to send your reason` may clarify an expectation.
  Keep any following `may have been lost` uncertain. Never replace `should
  have` with `must have`, `did`, or `cannot be sent without a reason` without
  evidence for the stronger claim. Keep `should have` when its counterfactual
  or advisory meaning is intended. Route missing behavior evidence to the
  outside-scope observations instead of inventing it.

Short labels can be fragments. Sentence-final prepositions and repeated words
are not defects by themselves. A repair such as changing `selected, with the
reason it was filed with` to `selected and shows the reason` adds a display
claim unless the UI confirms it. Keep legitimate contrast, duration, negation,
causal links and modal scope even when that requires a longer sentence.
