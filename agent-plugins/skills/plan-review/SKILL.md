---
name: plan-review
description: Review an implementation plan for feasibility and gaps without edits. Use review-spec for designs and code-review for diffs.
---

# Plan Review

Review an implementation plan against requirements, repository evidence, architecture, risks, and verification expectations. Do not edit files or rewrite the plan.

## Route exclusively

- Use this skill when the primary artifact is an implementation plan, including a plan revised during ongoing work.
- Use `code-review` when the primary request is to inspect changed code or a diff.
- Use `review-spec` when the primary artifact is a specification or design proposal rather than an ordered plan.
- Use `review-arch` for system architecture without an implementation plan, and `verify-impl` for completed code against a spec.
- Use `fix-pr` when the user asks to triage or apply GitHub pull-request feedback.
- If no plan can be identified in the request, conversation, or supplied file, ask for it instead of inventing one.

## Choose one mode

Use `quick` for a narrow plan with explicit requirements, `deep` for cross-component or uncertain work, and `final` for a release-readiness challenge. Honor a user-selected mode.

- `quick`: verify the goal, explicit requirements, referenced artifacts, and blockers. Keep the report compact, but include every material finding and verification limit.
- `deep`: also inspect applicable architecture, data flow, security, failure handling, tests, scope, and up to three useful local comparables. Include applicable architecture and failure-path evidence.
- `final`: assume the plan is nearly ready and try to break it with production edge cases, migration and rollback failures, concurrency, observability, and recovery gaps. Include release risks and their verification.

For `quick`, inspect only the plan, explicit requirements/instructions, and directly referenced files. For `deep` or `final`, inspect only enough repository context to verify material claims. Do not fill a comparison quota with irrelevant files.

## Load evidence

1. Identify the plan source and give each step a stable label if it lacks one.
2. Read applicable repository and path-scoped instructions.
3. Read explicit acceptance criteria, PRDs, issue text, or requirements supplied by the user or repository.
4. Verify referenced files, symbols, dependencies, commands, and directories.
5. Read comparable implementations only when the plan relies on a local pattern.
6. Record missing, inaccessible, or conflicting sources as limits; do not silently choose between conflicting authoritative sources.

Do not manufacture requirements or repository facts. When no explicit requirements exist, state that requirements traceability is limited to the stated goal and plan.

## Validate the plan

Check applicable concerns:

- each acceptance criterion maps to a plan step;
- steps do not add unrequested functionality;
- assumptions about current code and behavior match repository evidence;
- dependencies, interfaces, data ownership, and operation ordering are viable;
- security, privacy, authentication, and authorization boundaries are explicit;
- destructive changes include migration, rollback, and recovery;
- partial failures, retries, idempotency, concurrency, and edge cases are handled;
- tests and verification cover changed behavior and likely failure modes;
- safe parallel work is identified without obscuring dependencies;
- existing infrastructure is reused when it is the established fit.

Report only issues that improve correctness, safety, completeness, or maintainability. Omit preferences and speculative alternatives.

## Worst-case arithmetic

When the reviewed plan, specification, or architecture contains timeouts, deadlines, budgets, retries, pauses, backoff, rate limits, or queue or pool sizes, calculate the worst case step by step with concrete numbers. Consistent wording is not evidence that the promises are feasible.

1. Extract the stated limits, units, deadline start, scope of each budget, and every promise they support. Distinguish per-attempt caps, reserves for later work, and the overall task deadline. Use authoritative numbers; identify missing bounds or assumptions instead of silently inventing values or claiming a finite worst case.
2. List every step on each relevant path in execution order, including queue or slot waits, calls, pauses/backoff, retries, and work after a decision point such as follow-up, cleanup, or release. Give each step its maximum duration or resource use. Include a reachable case where an earlier step consumes its entire allowance.
3. At every decision point (retry or stop, continue or abort, acquire a slot or wait), calculate the remaining budget or free capacity, substitute the numbers into the actual proposed condition, and state whether it holds. Then account for all work permitted after that decision; passing a guard does not prove the remaining path fits.
4. Sum sequential costs and account for overlap under a reachable concurrent schedule. For queues, pools, and rate limits, calculate peak occupancy, held and requested slots, release order, burst arrivals per stated interval, and retry or fan-out amplification where applicable. Do not substitute averages for worst cases or add a reserve twice when it already represents the follow-up work.
5. Check every promise against those calculations, including "a timeout is retried", "N seconds remain for follow-up", and "the pool cannot be exhausted". Separate a condition that safely refuses work from a promise that the refused work will happen. If missing bounds prevent verification, state the exact missing input and leave the promise unverified.
6. Show the ordered calculation, decision conditions, and violated promise in the finding. A promise the numbers cannot satisfy is a blocking design contradiction even when the prose is consistent. A per-attempt cap, reserve, and task deadline that do not add up require a design correction, not merely tuning advice.

For example, with a 12 s task deadline, a queue wait capped at 2 s, attempts capped at 6 s, a 1 s retry pause, and 4 s of reserved follow-up work:

- After the full queue wait, `12 - 2 = 10 s` remain; a start condition `remaining >= attempt cap + reserve` holds: `10 >= 6 + 4`.
- After the first attempt times out, `12 - 2 - 6 = 4 s` remain. A retry condition `remaining >= pause + attempt cap + reserve` fails: `4 >= 1 + 6 + 4` is false.
- The promised retry path would require `2 + 6 + 1 + 6 + 4 = 19 s > 12 s`. Skipping the retry preserves the 4 s follow-up but contradicts a promise that every timeout is retried.

For a pool of two slots, if two workers each hold one slot and each must acquire another before releasing, free capacity is `2 - 2 = 0`; each acquisition needs `0 >= 1`, which is false. Waiting cannot fulfill an always-available-slot promise when release depends on that acquisition.

Apply this check in quick, deep, and final modes. Report a confirmed arithmetic contradiction as an open `P1` Blocker (or `P0` if its impact warrants it) and return `REVISE`; reserve `BLOCKED` for missing essential review evidence.

## Evidence and finding contract

Use stable IDs `PLAN-001`, `PLAN-002`, and so on. For every finding include:

- `Priority`: `P0`, `P1`, `P2`, or `P3`;
- `Disposition`: `open`, `question`, `accepted-risk`, or `not-applicable`;
- exact plan step and a short verbatim excerpt;
- requirement or repository evidence with `file:line` when available;
- concrete implementation risk;
- smallest plan-level remediation or a precise question.

Priority meanings:

- `P0`: the plan enables an immediate safety, security, or irreversible-loss hazard.
- `P1`: a blocker likely to make implementation incorrect, unsafe, or unrecoverable.
- `P2`: a material risk or missing behavior to resolve before executing the affected plan steps.
- `P3`: a small evidence-backed improvement.

Map report sections consistently: `P0` and `P1` open findings are Blockers; `P2` findings are Warnings; `P3` findings are Suggestions. Questions retain the priority of the risk they could reveal.

## Decide the verdict

- `APPROVE`: no unresolved finding or question that must be settled before executing the plan, and verification limits are acceptable. An open `P2` prerequisite requires `REVISE`, even in quick mode; optional `P3` suggestions need not block approval.
- `REVISE`: the plan is identifiable and reviewable but needs correctable changes before implementation.
- `BLOCKED`: the plan or authoritative evidence is missing, irreconcilably conflicting, or inaccessible enough that a responsible verdict cannot be reached. A dangerous plan with confirmed defects is `REVISE` with blockers, not `BLOCKED` merely because it is poor.

Never use `APPROVE` to mean that implementation itself has been verified.

## Report

Report plan identity, mode, sources and verification limits, followed by the verdict and findings ordered by priority. Use the same evidence fields in every mode; quick changes investigation depth, not whether material findings are visible.

For each finding use:

```text
PLAN-001 | P1 | open | <short summary>
Plan: Step <id>, "<short excerpt>"
Evidence: <requirement or repository file:line>
Calculation: <when applicable: ordered worst case, remaining budgets, and decision conditions>
Risk: <concrete implementation consequence>
Correction: <smallest plan-level change or precise question>
```

Include a compact requirements-to-step mapping with `Covered`, `Partial`, or `Missing` and supporting evidence. When no authoritative requirements exist, identify that limit instead of inventing criteria. In final mode also state remaining release, migration, rollback, and recovery risks.

Omit empty issue sections. If no issues remain, say so and preserve the verdict basis and verification limits. Do not edit, reorder, or replace the plan; checkout branches; install dependencies; or run state-changing commands.
