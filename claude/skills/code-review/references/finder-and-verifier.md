# Finder angles and reviewer roles

Use these procedures for standard and deep reviews. Quick scans hunks only and records that limit; it still separates candidate generation from verification and uses the same evidence requirements. Do not import or quote proprietary review prompts.

## Assign bounded passes

Count added plus deleted non-generated lines in the collected scope. Aim for roughly one finder pass per 150 changed lines, with at least one pass; partition by related functions/contracts rather than splitting a function at a line quota. Overlap only where a cross-file contract requires it. These are coverage passes, not a requirement to create that many agents.

The coordinator can find candidates. Reserve one fresh non-finder as verifier whenever an Agent tool is available; quick keeps it within the hunk-only scope. In deep, also reserve a different reviewer for the gap sweep when the budget permits. Use remaining agent capacity for independent finder partitions, and run remaining passes sequentially. Respect the repository's agent cap (at most three subagents here), one initial delegation wave, and roughly 30 model steps per agent; do not silently trade away required coverage to fit an arbitrary pass quota. State concrete limits when the scope cannot be covered.

Start reserved reviewers in that initial wave without finder history; send their inputs when ready. Do not fork the finder's conversation into the fresh verifier. Reuse the same verifier for sweep additions instead of launching a second assessment team. With only one available subagent, it can verify then sweep, while the coordinator verifies its additions because it did not find them. Without an Agent tool, separate the passes inline and explicitly report that independent verification and an independent sweep were unavailable. If the host or a stricter repository rule prevents delegation, disclose that constraint rather than claiming independence.

## Finder ledger

Assign a stable CR ID as soon as a candidate has a nameable failure scenario; coordinate disjoint IDs before parallel finding. Record its location, category, summary, scenario (`inputs/state -> wrong output, crash, or observable contract violation`), finder identity, and any missing premise. Preserve every such candidate until verification. Do not retract, rank by confidence, or replace a candidate with a question during discovery. Deduplication may link equivalent mechanisms without losing their distinct triggers.

Use these angles as procedures, not merely checklist labels:

1. **Hunks and enclosing functions.** Read the hunk and enclosing function, then trace normal and rare/error paths. Include defects in unchanged lines when the change re-exposes them or the change's stated repair should have fixed them. Name that connection; unrelated historical debt remains excluded. Cite the current failing line even when outside the hunk.
2. **Removed behavior.** For every deleted or replaced line, name the invariant, effect, or check it enforced and locate where the new code restores it. A mechanical or non-semantic removal can be recorded as such. Otherwise, no replacement means a candidate: a dropped guard, error path, validation, cleanup, or deleted test may expose a concrete failure or remove the only check of a required contract. Keep the before/after evidence for verification; absence alone does not prove a runtime defect.
3. **Cross-file contracts.** Find callers of each changed function and check new preconditions, changed return shapes, new errors, and ordering. Follow callees changed in the same diff and check the combined behavior, not just each isolated patch. Include callback and interface implementations where dispatch hides the direct call.
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

Return one assessment for every candidate, including refuted ones, with reviewer identity, quoted file/line evidence and the verdict. For `PLAUSIBLE`, include a concrete confirmation step. For `REFUTED`, identify one of: contradicting code, an impossible invariant/type, a guard in this diff, or a trace proving no observable effect. Show why it covers the proposed trigger, not just the normal path. A missing rule quote invalidates a conventions finding as unsupported policy; retain that rejection in the audit record without pretending it proves a runtime path safe.

Timing/configuration dependence is sufficient for `PLAUSIBLE` when the repository establishes the mechanism. Only hypotheses with an essential premise outside the repository belong in Questions. Missing local inspection is an unfinished verification step or disclosed limit, not external evidence.

In standard, the independent verifier supplies the disposition. In deep, one evidence-bearing non-`REFUTED` verification vote keeps the finding; do not use a majority vote or confidence threshold to erase it. If another reviewer provides conflicting refutation evidence, retain it as `PLAUSIBLE` and show the conflict and resolution check. A bare finder nomination is not a verification vote, and unsupported conventions still fail the quoted-rule gate.

## Deep gap sweep

After verification, give the sweep reviewer the same diff/files/intent and the verified findings list, including refutations to avoid rediscovering settled candidates. Ask only for new defects, not a second verdict on the whole list. Inspect:

- moved or extracted logic that lost a guard or regex/allowlist anchor;
- a lock whose scope shrank while protected work moved outside it;
- predicates whose side effects alter later decisions or state;
- test setup/teardown that no longer restores the same resources, globals, or configuration;
- flipped configuration defaults and the supported paths that now use them.

Add at most eight distinct candidates, without padding. Route them through the same three-outcome verification by someone other than their finder; give that verifier their scenarios and source, not sweep reasoning. Merge by failure mechanism and retain original CR IDs. Stop after this sweep and verification; do not recursively sweep new findings.
