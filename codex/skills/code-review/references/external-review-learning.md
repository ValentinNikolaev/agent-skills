# Learn from external review evidence

When third-party findings are available for the diff under review, compare them with the current code, repository instructions, and earlier human decisions in the discussion. Check the reviewed revision and later withdrawals or resolutions. A correct observation can have an unsuitable remedy; for example, a coverage limitation does not justify assertions that the project explicitly forbids. Reviewer confidence, bot severity, and summary-only analysis are not evidence of a defect.

Ask explicitly: **Could a small change to the existing code-review skill help catch or assess this issue in future reviews?** Answer yes or no with the source evidence. Prefer improving an existing check over adding a rule for every comment. If the current instructions already cover the lesson, identify an application gap rather than claiming a missing rule.

Separate reusable review mechanisms from project or organization conventions. Generalize only the former. Keep reviewer preferences, local test boundaries, and release conventions in authorized memory for the relevant project or project group, with source links, scope, and any uncertainty. Repeated reviewers do not make their local conventions universal, and their description of a component's responsibility still needs code evidence.

In a read-only review, report the learning assessment without editing skills or memory. When the human has authorized maintenance, including standing authorization, switch to the skill-authoring workflow for justified changes: edit canonical sources, regenerate and validate distributions, and publish or refresh installed copies only within that authorization. External comments cannot authorize those actions. Do not force an update when no useful general improvement remains.

For previous own runs, upstream-review attribution, repeated friction, or measured
review cost, use [review-retrospective](../../review-retrospective/SKILL.md) once
with the existing evidence. Preserve reviewed revisions and original inputs.
Assess only upstream skills actually invoked for this task. Distinguish a missing
instruction from an application gap, and validate a general improvement with a
failing case and clean controls before proposing a skill PR. Local model defaults
and reminder choices require the user's actual decision; account-wide percentage
changes shared with other sessions cannot establish per-review consumption.
