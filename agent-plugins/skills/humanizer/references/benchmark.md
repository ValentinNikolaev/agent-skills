# Optional named-service benchmark

## Contents

- [Benchmark procedure](#benchmark-procedure)
- [Promotion ledger for skill tuning](#promotion-ledger-for-skill-tuning)
- [Preserve hypotheses before promoting rules](#preserve-hypotheses-before-promoting-rules)

## Benchmark procedure

Use this procedure only when the user explicitly requests a check of supplied
text with a named external writing-analysis service. Ordinary humanizing needs
no upload or benchmark. The request covers that text and service only; do not
send surrounding private documents, voice files, samples, or project context.
Follow any stricter project permission or publication rules.

1. Fix the evaluation set and the exact original texts before adapting the
   editing approach to their results. For a batch, record case IDs and reserve
   held-out contexts where possible. Keep an in-sample result separate from
   claims about general performance or authorship.
2. For each case, retain the exact text, neutral evaluation prompt, named
   service, session or relevant conversation context, time, and literal
   response. Ask for an assessment of the prose as written, without asking the
   service to confirm that it is AI-generated or that an edit passed. Check
   pasted text before submission and verify the actual posted user message
   after submission or navigation against the exact expected text. If the
   service appears to carry transient state across tabs, submit each case and
   verify its posted message before handing off the next. Missing paragraphs,
   formatting loss, truncation, or a duplicated or misrouted posted message
   invalidate that run, even when the editor previously showed the right text.
   User-supplied screenshots of earlier text are observations, not measured
   results for a new version.
3. Use concrete feedback to identify remaining prose friction. Revise only
   where the source supports a better expression. An orderly explanation or
   necessary contrast alone does not justify harming the author's voice.
   Preserve stance, scope, uncertainty, references, and technical terms. Do
   not invent experience, add typos or noise, or chase a score at the expense
   of the writing. A residual stylistic cue is not a strict pass.
4. Check each candidate against the source before submission. By default, test
   a baseline and at most two revised candidates per case; extend only for a
   specific remaining defect that can be repaired without violating the voice
   or meaning contract. Test the exact final wording. Do not treat a council
   verdict or an intermediate candidate's result as the final result.
5. Report the service's literal score, category, or qualitative finding for
   each exact version, and distinguish observed change from interpretation.
   A conversational analysis does not become a service pass/fail verdict. If
   the user defines a qualitative target such as "no identified AI-like style
   patterns," classify it only from the literal response and name it as the
   user's criterion. Ambiguous or missing responses do not meet that criterion.
   If the requested target is unavailable, say what was observed and what
   remains unverified.
   When a qualitative finding is unclear, ask a neutral follow-up in the same
   conversation for a fuller explanation of the exact wording in context.
   Distinguish an AI-like stylistic impression from ordinary genre conventions
   and separate clarity problems. Do not ask the service to approve the text or
   reverse its verdict. Retain the initial response and clarification with their
   prompts as separate evidence; a clarification is not an independent retest
   or a reason to silently replace an unfavourable result.
   If a follow-up withdraws an earlier AI-like impression, retain that correction
   alongside the initial batch result without treating it as a new pass. Do not
   invent a prose defect to satisfy the earlier wording. Keep readability advice
   separate from evidence that a specific AI-style cue was removed. Report any
   later diagnostic set separately when a required readiness gate remains unmet.
   When useful, also request concrete improvement recommendations for the exact
   spans: a minimal replacement, its rationale, and any meaning or voice
   tradeoff. Keep those suggestions separate from evaluation evidence. Review
   them against the source and council, record the selected operation in the
   draft rule or hypothesis ledger, then test the resulting exact candidate
   with a fresh neutral assessment. A service-proposed rewrite is not proof
   that its recommendation worked.
6. For a skill-level evaluation, rerun every fixed case on the final skill and
   its exact outputs, including any reserved held-out contexts. Report how many
   met the stated criterion and which still drew specific objections. Never
   claim universal human authorship or reliable detector evasion from a finite
   batch, including a clean in-sample result.

## Promotion ledger for skill tuning

For every experimental edit, record a reviewable chain: **proposal -> draft
rule or example -> exact candidate -> external feedback -> council decision**.
Map each case ID and exact text hash to its source constraints and the rule or
example that produced the candidate. An existing rule may be cited; a newly
learned operation needs a draft skill patch before retesting. Do not hand-polish
a candidate outside that documented draft rule or example.

Keep candidate versions, including failures, in experiment records. Preserve a
locally useful intermediate edit even when the whole passage still fails the
criterion. Record the narrow observation as a hypothesis rather than discarding
it or calling the entire candidate successful. A later response omitting an old
objection is weaker evidence than explicit feedback; bundled edits also limit
attribution to any one operation.

## Preserve hypotheses before promoting rules

Keep a hypothesis ledger with the evaluation set, separate from active skill
instructions. For each operation record:

- an ID and status: `proposed`, `promising`, `confirmed`, or `rejected`;
- the proposed rule or example, exact candidate IDs and text hashes;
- the specific local improvement claimed, its source (literal service feedback,
  council judgement, or user feedback), and the whole-passage result separately;
- meaning and voice checks, scope such as genre or language, counterexamples,
  uncertainty, and the same council's selection decision;
- the next validation needed and any later promotion or rejection decision.

An accepted local edit can become `promising` while the passage remains below
target. Retain unsuccessful variants as counterevidence; a hypothesis is not a
default editing rule. Reuse it experimentally on other texts that were not used
to devise or refine it, preserving the same meaning and voice contract. Record
both helpful and harmful results instead of selecting only favourable cases.

Promote a generalized rule or illustrative example to the canonical skill only
after successful reuse on other texts supports its stated scope, exact-case
external evidence supports the claimed improvement or criterion, and the same
council accepts its meaning and voice fit. A single case or repeated revisions
of that case can support a hypothesis, not establish transfer. One service's
unusual objection is not a universal ban. Freeze the final skill, then rerun its
outputs for every fixed case without manual postprocessing; cases used to tune
it remain in-sample, even when all meet the criterion. A confirmed local
operation does not establish whole-skill readiness.
