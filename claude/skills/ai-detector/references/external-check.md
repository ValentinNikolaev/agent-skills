# External analysis of exact prose

## Contents

- [Verify the account and reasoning mode](#verify-the-account-and-reasoning-mode)
- [Submit and verify](#submit-and-verify)
- [Obtain actionable advice](#obtain-actionable-advice)
- [Interpret and stop](#interpret-and-stop)
- [Clean up ChatGPT conversations](#clean-up-chatgpt-conversations)

Use this reference for a human's explicit detector request. Workflow-only calls
remain local. The default service is
[ChatGPT AI detector](https://chatgpt.com/writing/ai-detector/).
The account and reasoning-mode procedure below applies to ChatGPT runs. For an
explicitly selected different provider, inspect its account/plan and supported
analysis controls instead, retaining unavailable model/effort values as unknown.
Do not open ChatGPT or divert the passage there to satisfy this procedure.

## Verify the account and reasoning mode

Complete this check before entering the passage into a surface that may submit
during navigation. Reuse observations from the same active task/session while
they remain current; recheck after an account, workspace, or access change.

- Inspect the signed-in ChatGPT account and active personal or managed
  workspace. Use the account menu and, if needed, subscription/settings view
  to identify the plan. Keep only a masked account identifier, workspace, plan,
  observation time, and relevant access/limit notices in the authorized evidence.
  Do not inspect billing details. Browser profile names, the Codex login/plan,
  and a model's self-description do not establish the ChatGPT account or plan.
- Use the account/workspace specified by the user or owning workflow, selecting
  an already authorized matching session when available. If none is available,
  stop before uploading and report the mismatch. Do not switch to an unrelated
  account/workspace or buy/upgrade a plan to obtain higher limits. When no account
  was specified, use the verified active session. An unverifiable identity leaves
  submission incomplete; an unavailable plan label stays `unknown` and must not
  be guessed from model availability.
- Unless the user explicitly selects another mode, choose a reasoning-capable
  model and set effort to `High` in the actual model/thinking controls. Select
  the model first, then verify its effort. On an older UI, use a documented
  equivalent such as `Thinking` with `Extended` thinking time. `Thinking` alone,
  `Instant`, `Auto`, or asking the model to "think harder" does not verify High.
  A Pro subscription does not require selecting the Pro model or higher effort.
- Check the options and limit notices actually available to this account and
  workspace. Plan eligibility alone does not prove current access. If the
  required model/effort is unavailable, quota-limited, or unverifiable, finish
  the local assessment and report the external check as incomplete. Use a lower
  mode only when the user has explicitly authorized it, and label that limit.
- If the writing page has no model controls, first prepare a ChatGPT chat on
  the same service with the required model/effort, then use the assessment prompt
  below with the exact passage. Do not auto-submit through the writing page
  and try to correct the model afterward. If no controllable route is available,
  leave the external check incomplete. Keep both the entry URL and actual chat
  link in the evidence.

Use the live UI for availability and current official documentation when labels
or eligibility are unclear. As of 2026-11-09, OpenAI documents `High` as extended
thinking and says availability depends on plan and workspace settings in
[models and thinking levels](https://help.openai.com/en/articles/20001354-gpt-6-and-other-models-in-chatgpt).
This is a configuration requirement, not measured evidence that High improves
authorship-detection accuracy.

## Submit and verify

1. Freeze the exact text and its meaning/voice constraints. Keep the local
   assessment separate, rather than asking the service to endorse it.
2. Open the service through an available authorized browser or supported tool.
   Read the current UI and complete the account/model check above. Do not assume
   an API, numeric score or fixed selector.
   For ChatGPT, use a fresh conversation for this check and track each created
   conversation by its actual URL or ID so cleanup cannot target an existing
   user conversation. Track invalid and incomplete attempts too.
3. Request an assessment and improvement advice neutrally. For example:

   > Assess the prose in TEXT for AI-like stylistic patterns in its genre.
   > Point to specific phrases and explain what, if anything, could improve.
   > Suggest minimal edits with reasons and meaning or voice trade-offs.
   > Identify wording worth keeping. Preserve the supplied factual, language
   > and voice constraints. Distinguish stylistic impressions from authorship.

   Delimit TEXT clearly. Send the passage, not its surrounding private files.
4. Prefer a non-submitting editor fill or paste for multiline text. Verify the
   entire passage before submitting. Some writing-page actions carry text into
   a chat or submit during navigation. Do not keep typing into a stale editor.
5. Verify the actual posted message against the expected passage after the
   transition. Check paragraph coverage and the first and last sentences, as
   well as exact text when available. A screenshot of an editor does not prove
   that the same text reached the service. A run that analysed instructions,
   omitted the passage or submitted a different version is invalid.
   Recheck the account/workspace and selected model/effort in the destination
   chat, including any response-level model metadata or fallback notices offered
   by the UI. A known downgrade does not complete a High-mode check. Keep that
   attempt and its literal feedback with the limitation; do not relabel it.
6. Wait for a completed response, without losing responsiveness to the user.
   Retain the service URL, session link, time, exact submitted text or its
   authorized evidence reference, prompt, account/workspace, plan, selected
   model/effort, any observed response-level model/fallback, and literal feedback.
   Distinguish a verified selection from unavailable backend model metadata.
   Do not claim that a request, partial response or local assessment is a
   completed result.

## Obtain actionable advice

The response must include improvement guidance, or explicitly find no useful
edit. If it gives only a score or broad category, ask a neutral follow-up in the
same session for exact spans, minimal replacements, reasons, and trade-offs.
This is clarification of the initial result, not an independent retest.

Separate three kinds of feedback:

- Stylistic impression and its concrete textual basis.
- Ordinary clarity or precision issues, which are not evidence of AI authorship.
- Useful conventions, idioms or qualifications that should remain unchanged.

Keep an initial finding and any later withdrawal or qualification together.
Do not ask the service to reverse a verdict or silently replace an unfavourable
response with its clarification. A model-proposed rewrite is not proof that it
preserves meaning, fixes the stated issue or passes a new check.

## Interpret and stop

Report literal scores and categories only when supplied. A qualitative response
does not imply a numerical result or a pass. If the user supplies a target such
as "no identified AI-style patterns", classify it only from the actual response,
and name it as the user's criterion. Missing or ambiguous feedback is unresolved.

Ordinary direct analysis checks one exact version. Do not reroll unchanged text
for reassurance. If the user requests comparison or authorizes skill tuning,
retain the baseline and test at most two supported revised candidates per case.
Extend only for a concrete unresolved defect within the user's scope. Each
candidate needs its own exact-input verification and literal result.

An explicitly local-only request overrides this external route. A blocked login
or unavailable page leaves the external result incomplete. Do not bypass an
access restriction, silently choose another provider, or describe local findings
as if the website returned them.

## Clean up ChatGPT conversations

Treat cleanup as the final step for every ChatGPT run, including an early stop,
failed submission, invalid attempt, or interrupted analysis. This applies only
to conversations created for the current check, never pre-existing user chats
or the conversation from which the skill was invoked.

1. Before cleanup, capture the available result, exact-input verification, and
   relevant limitations in the answer being prepared or an already authorized
   report. Do not create extra logs or exports just to enable deletion. A
   captured session URL is provenance, not a promise of continued access.
2. Delete each tracked conversation through an available supported control.
   Verify the target URL or ID before confirming deletion, then verify the
   observed outcome. Closing a browser tab does not delete a conversation.
3. If deletion fails or is unavailable, archive that conversation and verify
   the outcome. Archiving is the fallback, not evidence of deletion. Do not
   repeat failed actions indefinitely or use bulk delete/archive controls.
4. Report the actual cleanup status. If neither action succeeds, identify the
   remaining session link and the blocker. Do not claim cleanup from an
   unverified click. An incomplete analysis and a cleanup failure are separate
   limitations, and both must remain visible when applicable.

Cleanup does not require keeping a chat for a source link. Return the service
link and captured findings instead of a dead deleted-session link. An archived
session may remain as a provenance link, labelled archived.
