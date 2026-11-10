# Operator walkthrough for screen changes

Shared by `plan-review`, `review-arch`, and `review-spec`. Each skill decides when the walkthrough applies and what its conclusions mean for its own verdict; this procedure is the common method. The artifact under review is a plan, a design, or a specification.

## Scenarios

Walk every applicable operator scenario step by step: finding a record, filtering, assembling a change set, checking it, making a mistake and correcting or cancelling it, submitting, and viewing history. Use concrete valid and invalid inputs and empty data, not just labels such as "error case". At each step state the visible feedback and the next reachable action. Mark a scenario not applicable only with a reason grounded in the reviewed scope or boundary.

## Control challenges

Challenge every control the artifact adds: is it needed, will the operator find it, does its label and enabled/visible state match the current data, and can the operator recover? Check:

- disabled save/submit actions for a visible explanation associated with the input (for example `aria-describedby`), and field-associated validation feedback;
- Resume with nothing to resume;
- Add for an already-added row;
- explicit ordering of selection lists;
- back and cancel paths through dialogs.

Report a concrete dead end even when the artifact deliberately prescribes it.

## Table

Return a table `Step → Plan/design/spec section → Verdict`:

- Step: the concrete input or state and the expected visible feedback and next action;
- middle column: the section or excerpt that is the evidence;
- Verdict: `Covered | Partial | Missing | Defect | Not applicable`, plus any finding ID (`PLAN-`, `ARCH-`, or `SPEC-`).

Label this a document walkthrough, not executed UI testing. Mark underspecified behavior or unspecified recovery as a gap.

## Event-catalog example

User-reported case: Save was disabled because parsing accepted only `DP-N` and `catch { return null }` swallowed the error. Another project's key and a board URL with `?selectedIssue=OTHER-42` silently blocked saving. Walk `DP-42`, `OTHER-42`, that board URL, `DP-x`, and empty input through the artifact's parse, feedback, save-state, and cancel steps. "Disable Save on parse failure" without visible feedback is a dead end to report.
