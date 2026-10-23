# Optional named-service benchmark

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

Keep failed edits in experiment artifacts only. Promote a generalized rule or
illustrative example to the final canonical skill only when the exact-case
external result improves or meets the chosen criterion and the same council
accepts its meaning and voice fit. One service's unusual objection is not a
universal ban. Freeze the final skill, then rerun its outputs for every fixed
case without manual postprocessing; the cases used to tune it are in-sample,
even when all meet the criterion.
