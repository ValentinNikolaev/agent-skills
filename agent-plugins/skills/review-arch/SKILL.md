---
name: review-arch
description: Review system boundaries and architecture tradeoffs; not line-level code review.
---

# Architecture Review

Assess the architecture of a named system, subsystem, or design decision. Report structural risks grounded in the system's actual goals and constraints. Do not edit code or create a report file unless requested.

## Route precisely

- Use this skill when the question concerns system structure, ownership, dependency direction, integration topology, or quality tradeoffs.
- Use `review-spec` when a proposed specification or revision is the primary artifact and the question is whether its design is sound.
- Use `verify-impl` for requirement-by-requirement conformance of existing code to a spec.
- Use `code-review` for correctness of changed lines and ordinary pull-request readiness. A changed architecture may warrant both reviews when explicitly requested, with separate scopes.
- Use `plan-review` for an ordered implementation plan.

## Build a bounded model

1. Name the system boundary, users, purpose, scale, deployment environment, and known quality priorities. Source these from the request and directly relevant documents; mark unknowns instead of assuming enterprise-scale needs.
2. Read applicable repository instructions, architecture documentation and decisions, and representative implementation paths. Follow data and control across the boundaries under review.
3. List the major decisions actually present: component responsibilities, data ownership, communication, persistence, failure isolation, deployment, and operational ownership. Record explicit deferrals.
4. Form at least one realistic scenario that stresses each material quality goal, such as a partial dependency failure, simultaneous updates, or increased load. State the scenario's assumptions.

## Evaluate decisions

For each consequential decision, assess:

- whether it serves the stated business and user goals;
- which quality attribute it improves and what it costs elsewhere;
- whether component boundaries and dependency direction preserve clear ownership;
- whether data consistency, failure recovery, security boundaries, and observability are credible for the scenario;
- whether a simpler architecture meets the same constraints;
- whether an apparent anti-pattern has a concrete failure mode here rather than merely matching a label.

Ground each finding in a file, diagram, decision record, requirement, or observed runtime behavior. Trace the consequence through a plausible scenario and check for mitigations. Do not infer operational needs solely from a methodology or demand every quality attribute be maximized. If a key priority is unknown, present the conditional alternatives and the decision needed.

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

Report a confirmed arithmetic contradiction as a critical risk with verdict `CONCERNS`, explicitly blocking the affected architecture decision until corrected. Do not return `SOUND` for that decision or use `BLOCKED` merely because the design is defective; reserve it for missing essential context.

## Go lifecycle, when applicable

For Go systems, trace ownership of background goroutines, shared state, connections, and shutdown across package boundaries. Check whether fan-out, queued work, retries, and partial failures remain bounded under the stated load. Judge flat packages, `internal/`, architectural layers, and DI containers by their observed dependency/lifecycle cost; none is a defect by name. Reuse the same scenario-based evidence standard instead of requiring a particular Go architecture.

Selected Go lifecycle considerations adapt [Samber's design-pattern guidance](https://github.com/samber/cc-skills-golang/blob/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717/skills/golang-design-patterns/SKILL.md), under the bundled `LICENSE.samber-cc-skills-golang`.

## Report

Return the reviewed boundary and evidence, then a verdict of `SOUND`, `CONCERNS`, or `BLOCKED`. `BLOCKED` means essential context is unavailable. Group evidence-backed findings as critical risks, significant concerns, and observations; give each the triggering scenario, impact, and smallest useful decision or experiment. Include sound decisions worth preserving, open questions, and verification limits. A structural concern does not automatically block a small code change; state what decision it affects.
