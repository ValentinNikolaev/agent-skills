# Plan review cost examples

| Request or condition | Before | After |
|---|---|---|
| Same plan is reviewed for specification, architecture, and execution | Three agents re-check general feasibility and all derive worst-case retry timing | `plan-review` owns step dependencies, requirements-to-step mapping, execution verification, and ordered timing/capacity calculations; specification coverage/testability and structural alternatives have distinct owners |
| Plan implements an accepted storage boundary | Re-open the architecture choice and propose unrelated alternatives | Check that the steps respect the accepted boundary and rollback requirements; flag a conflicting step without redesigning the system |
| `shared_context=_coord/PROJ-123/code-facts.md` provides revision-pinned symbols, excerpts, and schemas | Re-read every referenced file and comparable | Reuse those facts, verify only doubtful or missing material claims, and name reused evidence and fresh checks in the report |
| Supplied schema excerpt lacks the uniqueness constraint needed by step 3 | Assume the context file proves every claim | Inspect just the disputed schema/constraint and record what remains unverified; repository instructions still apply |
| `light`: a single-repository UI plan, no concurrency/storage changes, research already identifies components | Re-derive the research and expand into a deep review | Reuse the research, map requirements to steps, and report at most five prioritized findings with unchanged PLAN fields and verdict rules |
| Light review discovers seven issues including a P1 blocker and P2 prerequisites | A cap hides the blocker or suggests approval | Show the five highest-priority findings, disclose two omitted, and return `REVISE` based on all discovered issues; do not launch a new review automatically |
| Light plan states a 12 s deadline and already derives a 19 s retry path | Re-read source facts and repeat an established derivation | Cite the supplied derivation in `Calculation`, verify its disputed/changed conditions only, and retain a P1 Blocker with `REVISE` |
| Light plan lacks a calculation for a promised bounded operation | Skip budget checks to make light cheaper | Use established research inputs to perform the missing calculation; do not invent missing bounds or re-derive established code facts |
| `light` requested for cross-repository work or changed concurrent/storage behavior | Treat a short plan as eligible | Explain why light is ineligible and use quick; honor an explicitly requested deep/final review instead of silently downgrading it |
| Caller selects a model for a plan review, including `light` mode | Pick a cheaper model because the plan is short | Recommend the top model for every plan review; the skill itself never selects or switches models |

Routing examples: an ordered implementation plan activates `plan-review`, including with `shared_context=...` or `light`. A requirement proposal without implementation steps activates `review-spec`; a system-boundary/alternatives decision activates `review-arch`; implemented diff defects activate `code-review`. Do not automatically fan one request out to three reviewers.

The 12 s deadline / 19 s retry path and two-slot hold-and-acquire examples in `SKILL.md` remain the quantitative controls.
