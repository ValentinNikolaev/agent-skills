# Finder angles and reviewer roles

Use these procedures for standard and deep reviews. Do not import or quote proprietary review prompts.

## Assign bounded passes

Agent assignment belongs only to the top-level coordinator. Include the no-nested-delegation boundary and the main skill's read-only execution rule in every assignment.

Count additions plus deletions separately as `P` for production/configuration/other non-generated files and `T` for test-only files, using the repository's test conventions. Exclude generated bulk with its source and reason recorded. Count executable test infrastructure or fixtures at full weight in `P` when their complexity or risk warrants it, without also counting those lines in `T`. A test filename alone does not justify discounting production behavior.

For standard and deep, use weighted volume `W = P + 0.25 * T` and advisory demand `D = max(1, ceil(W / 600))`. This is a scheduling heuristic, not a required number of rereads or a quality measurement. Quick keeps its hunk-only scope and does not inherit this volume target.

Before assigning passes, set `A` to the direct subagent slots actually available under both the host and repository limits, capped at three here. Reserve `V = 1` fresh non-finder verifier when `A >= 1`, otherwise `V = 0`. In deep, also reserve `S = 1` separate sweep reviewer when `A >= 2`, otherwise `S = 0`; standard uses `S = 0`. With the coordinator performing one finder partition, finder capacity is `F = 1 + A - V - S`. Plan `B = min(D, F)` baseline finder passes and record this capped plan before discovery. A verifier or gap sweep does not count as a baseline finder pass. Respect one initial delegation wave and roughly 30 model steps per agent.

Partition all changed non-generated paths and hunks among those `B` passes by related functions/contracts, keeping tests with the behavior they exercise. Review every changed test despite its lower scheduling weight. Keep enclosing-function, removed-behavior, caller/callee, wrapper, repository-rule, and shared-mechanism checks within each applicable partition. Overlap only for cross-file contracts; rereading the same partition or invoking another agent alone is not another coverage pass.

Record `P`, `T`, exclusions/full-weight exceptions, `W`, advisory `D`, available/reserved roles, planned `B`, completed passes, and the file/function partition ledger. The report's required pass denominator is the capped plan `B`, not `D`. `D > F` is budget saturation, not an automatic coverage deficit. A missing planned partition, unread changed hunk/test, or omitted applicable trace is an actual deficit: name the affected paths and checks rather than treating a capped count as proof of coverage. Prioritize state machines, concurrency, and identity/ownership. If the partitions cannot be covered within the initial budget, make a bounded sequential extension with the same agents when authorized or disclose the concrete coverage limit; never mark uninspected work complete or start another delegation wave just to meet the volume estimate.

For example, `P = 1594`, `T = 762` gives `W = 1784.5` and `D = 3`. With three available subagent slots, standard reserves one verifier and plans three finder passes including the coordinator. Deep reserves a separate sweep reviewer too and plans two baseline finder passes plus its gap sweep. The raw 2356 changed lines do not set the pass count; the weighted demand and available roles do. Passing this arithmetic does not establish review recall or the correctness of any finding.

Start reserved reviewers in that initial wave without finder history; send their inputs when ready. Do not fork the finder's conversation into the fresh verifier. Reuse the same verifier for sweep additions instead of launching a second assessment team. With only one available subagent, it can verify then sweep, while the coordinator verifies its additions because it did not find them. Without an Agent tool, separate the passes inline and explicitly report that independent verification and an independent sweep were unavailable. If the host or a stricter repository rule prevents delegation, disclose that constraint rather than claiming independence.

## Finder ledger

Assign a stable CR ID as soon as a candidate has a nameable failure scenario; coordinate disjoint IDs before parallel finding. Record its location, category, summary, scenario (`inputs/state -> wrong output, crash, or observable contract violation`), finder identity, and any missing premise. Deduplication may link equivalent mechanisms without losing their distinct triggers.

Use these angles as procedures, not merely checklist labels:

1. **Hunks and enclosing functions.** Read the hunk and enclosing function, then trace normal and rare/error paths. Include defects in unchanged lines when the change re-exposes them or the change's stated repair should have fixed them. Name that connection; unrelated historical debt remains excluded. Cite the current failing line even when outside the hunk.
2. **Removed behavior.** For every deleted or replaced line, name the invariant, effect, or check it enforced and locate where the new code restores it. A mechanical or non-semantic removal can be recorded as such. Otherwise, no replacement means a candidate: a dropped guard, error path, validation, cleanup, or deleted test may expose a concrete failure or remove the only check of a required contract. Keep the before/after evidence for verification; absence alone does not prove a runtime defect.
3. **Cross-file contracts.** Find callers of each changed function and check new preconditions, changed return shapes, new errors, and ordering. Follow callees changed in the same diff and check the combined behavior, not just each isolated patch. When an existing call moves after side effects, re-check its callee's failure semantics under the new preconditions; best-effort logging acceptable before those effects may abandon committed work afterwards. Include callback and interface implementations where dispatch hides the direct call.
4. **Wrappers, decorators, caches, and adapters.** Enumerate methods callers use, verify that each is forwarded, and trace the receiver to the wrapped instance. A route back through a registry or global may recurse, choose a different instance, bypass state, or lose configuration. Name the affected call and wrong behavior; an intentional registry lookup with equivalent semantics is not a defect just because of its shape.
5. **Repository conventions.** Locate and quote the exact binding rule, its file path, and the violating source line. State the observable contract or maintenance consequence. Unsupported conventions are rejected during verification; preferences do not become rules because several files look similar.
6. **Level of the fix.** Trace a special case added to shared infrastructure to the mechanism responsible for the failure. If fixing that mechanism would handle the affected paths while the special case leaves a concrete failure, record that scenario and the smallest mechanism-level correction. Do not turn this into unrelated architectural cleanup.

Keep the language and conditional checks, coverage mapping, and negative controls active on these paths. A supported error, cold-cache, optional-field, or partial-retry path is not out of scope just because the happy path avoids it.

## Verification handoff

Send the fresh verifier:

- the exact diff/base/head and relevant current and before-image files;
- intended behavior, authoritative instructions and rules;
- candidate IDs, finder identities, locations, summaries, and failure scenarios.

Do not send the finder's private reasoning, confidence, favored verdict, or proposed fix. The verifier reconstructs the evidence independently. A failure scenario is the hypothesis to test, not an instruction to accept it.

Return one assessment for every candidate, including refuted ones, with reviewer identity, quoted file/line evidence, and the verdict under the outcome rules in `SKILL.md`; a `PLAUSIBLE` assessment includes its concrete confirmation step and a `REFUTED` one names its refutation kind.

In standard, the independent verifier supplies the disposition. In deep, one evidence-bearing non-`REFUTED` verification vote keeps the finding; do not use a majority vote or confidence threshold to erase it. If another reviewer provides conflicting refutation evidence, retain it as `PLAUSIBLE` showing both pieces of evidence and the resolution check; never suppress it silently. A bare finder nomination is not a verification vote.

When a finding is confirmed, sweep the rest of the diff for the same failure pattern before moving on. Trace each sibling's trigger and guards, pass new candidates through the same verification, and report all affected locations, grouping only when the mechanism and remedy are shared. Keep distinct triggers and counterexamples; textual similarity alone is insufficient. This bounded search applies at every depth and stays within that depth's scope.

Regression example: one changed editor retains stale local state after its input changes, and four sibling editors copy the same initialization pattern. Confirm the input-change path in each and report all five affected locations. An editor that explicitly resynchronizes or is guaranteed to be recreated on the relevant transition is a clean control. Deduplication must not silently drop sibling locations.

## Deep gap sweep

After verification, give the sweep reviewer the same diff/files/intent and the verified findings list, including refutations to avoid rediscovering settled candidates. Ask only for new defects, not a second verdict on the whole list. Inspect:

- moved or extracted logic that lost a guard or regex/allowlist anchor;
- a lock whose scope shrank while protected work moved outside it;
- predicates whose side effects alter later decisions or state;
- test setup/teardown that no longer restores the same resources, globals, or configuration;
- flipped configuration defaults and the supported paths that now use them.

Add at most eight distinct candidates, without padding. Route them through the same three-outcome verification by someone other than their finder; give that verifier their scenarios and source, not sweep reasoning. Merge by failure mechanism and retain original CR IDs. Stop after this sweep and verification; do not recursively sweep new findings.
