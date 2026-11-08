# Model proposals and local decisions

Offer a downgrade only when comparable evidence suggests a useful saving for a
specific stage and risk class while preserving its required checks. Reuse the
project's configured model tiers. Explicit current user selection or a chosen
workflow profile takes precedence. Confirm availability before a future use;
never silently substitute a different model or reduce review depth.
Prefer a deterministic helper when the stage requires no model judgment. Omit
advice conflicting with an explicit selection unless comparative advice was
requested. Treat the proposal as a hypothesis until its evidence is sufficient.

Show at most one material proposal after the review result. A short card should
name the stage, current/target model and reasoning, evidence/sample limitations,
expected benefits, and disadvantages. Discuss quality/coverage risk, latency, and
usage tradeoffs that actually apply. Measured benefits and estimates must be
distinguishable; missing percentages remain unknown. Do not promise that a less
expensive model will necessarily finish faster. Prefer a bounded trial when the
evidence is too weak for a default. Omit low-value or suppressed suggestions.

Example wording, with the actual evidence filled in:

> For the mechanical scope-collection stage, consider <model/settings>. Benefit:
> <observed saving or explicitly estimated benefit>. Tradeoff: <quality/latency
> risk and check retained>. Evidence: <comparable cases and limits>. Apply this
> scoped default in this project?

Acceptance authorizes saving that scoped setting locally. Use an agreed project
policy path, for example `.review-learning/model-policy.json`; preserve existing
keys and unrelated defaults. Keep it out of global agent configuration. Do not
commit local preferences without authorization. A saved preference is input to
the caller's next model selection, not proof that the current runtime switched.

After refusal, ask once whether to remind about this proposal in a week or never
again. Ask after delivering the result, using an available asynchronous question
capability where suitable. An unanswered question stays pending and suppressed;
it is not consent to a reminder. Record an explicit reminder/dismissal choice in
the authorized local policy. Permanent dismissal suppresses this scoped proposal
across sessions until the user explicitly reopens it, including when new evidence
arrives. Do not turn dismissal of one proposal into a global refusal of all model
advice. Avoid repeated prompts about a pending choice.

A one-week choice is one reminder, not a weekly subscription. With an available
scheduler, create it only after that explicit choice, respect the user's timezone,
and confirm success before claiming it is scheduled. Without a scheduler, explain
that the record can surface once at the next review after the due date; it cannot
send a background notification. Mark the reminder shown after actual delivery.

The helper's `offer` and `decision` subcommands read an envelope containing
`policy` and `proposal` and print JSON only:

```json
{
  "policy": {"schema_version": 1, "defaults": {}, "decisions": {}},
  "proposal": {
    "skill": "code-review", "stage": "scope-collection",
    "risk_scope": "mechanical", "from_model": "current-model",
    "to_model": "candidate-model", "to_reasoning": "low"
  }
}
```

Resolve `<skill-dir>` to the directory containing the owning `SKILL.md`. Use
`python "<skill-dir>/scripts/review_learning.py" offer --input ENVELOPE.json --at
2026-11-08T12:00:00+01:00` before presenting a proposal. `decision` takes the same
arguments plus `--action accept|decline|remind-week|never|reminder-shown`.
`decline` records a pending reminder choice. `remind-week` sets one due date.
`never` dismisses the scoped proposal. `reminder-shown` consumes an eligible
reminder. These commands do not ask the user, save files, switch models, or create
automations. The caller obtains the actual choice, writes only the authorized
policy after checking current contents, and separately schedules any authorized
reminder. Preserve the proposal's evidence and pros/cons in the report.
