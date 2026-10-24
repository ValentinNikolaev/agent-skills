# Improving the detector and humanizer from feedback

## Contents

- [Choose the owner and authorized scope](#choose-the-owner-and-authorized-scope)
- [Apply the smallest supported correction](#apply-the-smallest-supported-correction)
- [Retain the evidence and test the change](#retain-the-evidence-and-test-the-change)
- [Promote only what the evidence supports](#promote-only-what-the-evidence-supports)

## Choose the owner and authorized scope

Use current task and standing authorization to decide whether maintaining these
skills is in scope. An analysis request alone is not general permission to
modify installed software or unrelated skill repositories. When skill upkeep is
already authorized, proceed without another approval question.

- `ai-detector` owns invocation mode, local analysis, external submission,
  feedback interpretation, exact-input verification, and actionable findings.
- `humanizer` owns supported prose edits and preservation of the author's
  meaning and voice. Leave author persona and project-specific editorial rules
  in their owning workflow.

Locate the authoritative sources and read their repository instructions before
editing. Preserve dirty overlapping work. Do not patch a generated distribution
or managed installed cache as the source of truth. If the source or authority is
unavailable, return a concrete proposed patch and the limitation.

## Apply the smallest supported correction

Repair demonstrated workflow defects immediately within authorized scope. For
example, a submitted message that omitted the passage supports a verification
and recovery correction in the detector. It does not support a prose-style rule.

For textual feedback, compare the service's exact recommendation with the source
and voice constraints. Keep a good phrase when the proposed alternative changes
the actor, modality, scope or conversational job. Improve a specific clarity
problem without labelling the whole text AI-written.

Apply a narrow reusable instruction or bounded example when the reasoning is
supported. Record a broader untested pattern as a hypothesis, rather than
silently making it a mandatory rule. Do not add synonym lists, fixed rhythm,
forced informality or a new ban for each isolated service preference.

If the text itself is in the authorized editing scope, let `humanizer` make the
necessary edit. Reuse the owning workflow's existing advisors and exact-copy
assessment where required. Do not create another council just for a local
detector finding. Do not claim that maintaining a skill also revised every
text that previously used it.

## Retain the evidence and test the change

Maintain a reviewable chain for each actual improvement:

> observed defect -> owner and proposed correction -> exact candidate or skill
> patch -> verification -> retained limits and counterevidence

Use the repository's existing evaluation records where available. Keep only
authorized evidence. Record case ID, exact input/version or hash, local
findings, external literal response and session, valid/invalid submission state,
accepted or rejected recommendations, affected skill paths and test outcomes.
Keep historical failures and withdrawals intact. A later successful candidate
must not overwrite its failed baseline.

For skill-level comparison, freeze the cases before tuning and reserve an
independent context when feasible. A registered fixture or valid JSON is not a
successful writing evaluation. Verify the observable routing and preservation
decisions, not just the presence of preferred phrases in instructions.

Run the owning repository's checks and regenerate managed distributions. Reuse
the initial reviewers for any necessary follow-up. When external retesting is
authorized, verify the exact final candidate with a fresh neutral assessment.
Report checks actually run, failures, skipped work and residual uncertainty.

## Promote only what the evidence supports

Use statuses such as proposed, promising, confirmed and rejected for uncertain
editing operations. Preserve meaning/voice constraints, counterexamples and the
next validation step alongside each hypothesis. A local improvement may be
promising while the whole passage still misses the user's criterion.

Promote a broad editorial rule only after independent reuse supports its scope
and the applicable editorial review accepts it. A concrete workflow defect can
be fixed from a reproducible failure without waiting for a large writing corpus.
Do not delay a safe, supported correction solely to collect more scores.

Do not equate convergence among models, a clean in-sample result, or a detector
score with proof of authorship or universal skill effectiveness. Rerun frozen
cases on the final skill when claiming a skill-level result. Stop when the
authorized correction and its necessary verification are complete.
