# Validate learning and model changes

Separate package/JSON checks from behavioral effectiveness. A helper accepting
an assessment does not prove that a model finds the defect, and an accepted bot
comment is not a labeled ground truth. Resolve or retain disputed evidence.

For a skill change, use a frozen original case, a near-neighbor clean control,
and a small held-out set covering other mechanisms. Keep evaluation-only answers
and retrospective diagnoses away from the reviewing agent. Compare old/new skill
versions with the same available inputs, model, settings, depth, and tools.
An upstream stage gets only information available before implementation.

For a model change, hold the skill and task conditions fixed. Use comparable
scope, risk, evidence access, checks, and tooling. Separate model latency from
CI waits, tool delays, warm/cold context, and repeated reads. Repeat a noisy
comparison only when it can change the decision within the authorized budget.

Assess verified findings, false positives, severity/verdict correctness, known
misses, and follow-up rounds alongside actual tokens, elapsed time, and comparable
usage snapshots. Measure recall only on labeled cases; unseen production misses
are unknown. Zero findings does not prove quality. A cheaper result that skipped
required checks is reduced coverage, not a demonstrated efficiency gain.

Preserve the original report and evidence, comparison settings, exact outputs,
evaluation limits, and total cost of the experiment. Do not claim a universal
speedup or saving from one incident. A trial can justify a limited experiment
rather than a project default. Protect confirmed critical cases and clean controls
before broadening a policy; state any observed regression.

For an application gap, first check whether a smaller entrypoint, a relevant
reference trigger, a deterministic validation gate, or a clearer handoff fixes
execution. Adding another universal checklist item needs separate justification.
For a project lesson, include its scope, sources, invalidation conditions, and
superseding decision. Never promote a local convention into a general skill rule.

For a PR proposal give the owning skill, concrete failure, minimal canonical
patch, sanitized failing/clean pair, behavioral comparison, and expected context
and maintenance cost. Keep private paths, organizational policies, and real
customer data out of the public patch. Existing canonical generation, validation,
versioning, and independent-review rules remain authoritative. Record a rejected
or ineffective candidate without appending a rule merely to complete the cycle.
