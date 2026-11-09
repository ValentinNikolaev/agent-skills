# Learning from completed prose passes

## Contents

- [Select evidence and preserve authority](#select-evidence-and-preserve-authority)
- [Link exact versions](#link-exact-versions)
- [Diagnose and choose an owner](#diagnose-and-choose-an-owner)
- [Validate a lesson](#validate-a-lesson)
- [Measure cost and propose model changes](#measure-cost-and-propose-model-changes)

## Select evidence and preserve authority

Use this procedure for completed `humanizer` and `ai-detector` runs when new user
feedback, verified meaning/voice drift, a missed wording defect, unnecessary
editing, invalid submission, or repeated iteration cost supplies a useful signal.
A maintenance request naming these skills does not request analysis or upload of
any passage. Ordinary editing retains its existing local/external routing.

Use [review-retrospective](../../review-retrospective/SKILL.md) for bounded case
selection, unchanged-evidence suppression, cost accounting, project model
decisions, and a concrete skill-PR proposal. This file and
[the improvement loop](improvement-loop.md) own prose-specific interpretation
and maintenance. Do not create another learning system or a council per lesson.

Keep existing project voice, language, genre, evidence and final-copy gates
authoritative. Record only authorized material in an already-requested report,
handoff, or approved journal. A text-only response stays text-only. No silent
transcript export, corpus building, voice-file edits, or local policy writes.
Retrieve only relevant accepted project lessons; a past preference cannot
override the user's current instructions or become a universal style rule.

## Link exact versions

Retain pointers to the original, locally edited, actually analyzed/submitted,
and delivered copies, plus brief, voice revision, language, genre, requested
operation, skill/model/mode, and feedback. Keep accepted/rejected suggestions
and useful keep decisions. Preserve failures and later withdrawals.

Use the common [run contract](../../review-retrospective/references/run-contract.md)
with an optional `prose` object. Retain these fields when available:

| Field | Evidence |
| --- | --- |
| `language`, `genre`, `brief_artifact`, `voice_artifact`, `voice_revision` | Original editing constraints and their validity |
| `input_text_sha256`, `output_text_sha256` | Humanizer's exact before/after UTF-8 bytes |
| `text_sha256` | Detector's exact analyzed text |
| `decisions_artifact`, `user_feedback_artifact` | Located recommendations, accepted/rejected/keep decisions, and corrections |
| `external` | For an external detector: `submission_state` (`valid`, `invalid`, `incomplete`), `submitted_text_sha256`, `provider`, `captured_at`, `result_artifact` |

Hashes are 64 lowercase hexadecimal characters, computed from exact UTF-8 bytes
without newline or Unicode normalization. Missing values are unknown. A hash
links versions; it does not prove the submitted message or feedback is valid.
Inspect actual source artifacts and, for external work, the actual submission.
External `captured_at` is an ISO 8601 timestamp with an explicit timezone. Missing,
`unknown`, empty, or malformed provenance cannot establish a valid comparison.

For a known paired pass, add `paired` with `skill`, `invoked`, `run_id`, and
`invocation_evidence`. A humanizer record may link an invoked detector, and a
detector record may link an invoked humanizer. Both must belong to the same task.
Unknown/false invocations are skipped. Missing artifacts or identities are
limits; differing edit/analyzed hashes invalidate that paired comparison.
Do not run a missing skill to complete the history. A detector-only analysis and
a humanizer-only edit are valid workflows.

Use detector mode `local` or `external`. Invalid/incomplete external submissions,
wrong text, unavailable feedback, or missing provenance cannot supply a valid
external comparison. Local findings remain usable on their own evidence.
Never reconstruct a numeric score from qualitative feedback or apply results
from an earlier copy to the delivered copy.

## Diagnose and choose an owner

Distinguish a missing instruction from ignored guidance, stale voice/brief,
mislinked text versions, unsupported detector feedback, tool/service failure,
and an excessive iteration/model budget. Verify the actual passage and reader
effect before promoting feedback. A rejection can reveal a local preference
without establishing a general editorial defect.

- `humanizer` owns introduced meaning/voice drift, unnecessary edits, and missed
  idiomatic or structural repairs within the authorized edit.
- `ai-detector` owns unsupported findings, missed local analysis, invocation
  routing, exact submission, feedback interpretation, and actionability.
- The project owns persona, channel conventions, language calibration, and
  context-specific preferences. Propose scoped updates to their existing owner.

Preserve modality, actors, uncertainty, attribution and protected spans even
when a service recommends changing them. A lower detector score is not better
writing. Service agreement, author labels, and a model's self-rating do not prove
authorship, quality, or a reusable improvement. Already-natural prose and a
rejected suggestion are valuable clean controls, not failures to edit.

## Validate a lesson

Freeze the original brief, voice/version and passage before tuning. Include a
failing case, a near-neighbor keep/no-edit control, and held-out cases varying
language, genre or length only when those scopes are claimed. Give independent
evaluators raw inputs without the desired rewrite, suspected defect, scores, or
prior conclusions. Evaluate the exact candidate that would be delivered.

Compare fidelity to facts, scope and intent, voice/register, idiomatic clarity,
coherence, unnecessary edits, false findings, missed editorial defects and
iteration count. Keep independent reader assessment separate from literal
external results. Preserve counterexamples and classify unsupported changes as
hypotheses. A structural fixture test does not establish editorial effectiveness.

Repair a reproducible workflow error narrowly within authorized maintenance.
An existing instruction ignored calls for a retrieval/execution improvement,
not a duplicate ban. Promote a broad editorial rule only with scoped independent
reuse. For a general improvement, propose the owning skill's minimal canonical
patch, sanitized failing/clean cases, observed comparison and limits. Publication
requires existing authorization; a project lesson does not belong in the public
skill merely because several drafts share the same author's preference.

## Measure cost and propose model changes

Capture available start/end and per-stage time, real tokens, calls, and identified
limit-window percentage snapshots through the common run contract. Separate
editing, local analysis, external waiting, and rechecks. Shared account deltas,
missing snapshots, or window resets cannot establish this passage's consumption.
Compare equivalent briefs, lengths, languages, depth and mandatory checks.

Use the common [model policy](../../review-retrospective/references/model-policy.md)
for at most one useful stage-specific proposal with short pros/cons, measured
benefits versus estimates, quality risks, and sample limits. Cheaper models must
still preserve meaning/voice and complete required checks. Respect explicit model
choices. Save a local default only after acceptance. After refusal ask once about
one reminder in a week or never; suppress pending/dismissed suggestions.

Stop when the concrete wording defect and required final-copy gates are resolved.
Do not keep rewriting, uploading, or re-running a council to chase a detector
metric. Reassess only new or changed evidence and stay within the authorized
iteration budget; a costly full comparison is separate bounded work.
