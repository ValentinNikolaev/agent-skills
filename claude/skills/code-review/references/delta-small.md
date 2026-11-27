# Small review-fix deltas

Use `code-review delta-small` or `--depth delta-small` for one fix round. Start with the previous review, its reviewed head, the proposed head, and the author's fix and mutation claims. Use an independent reviewer of the author's changes. The reviewer may discover and verify in separate passes inline.

## Decide whether the round fits

Compare the two pinned heads directly across all pushes in the round. Count added **plus** deleted physical production source lines, including imports, declarations, JSX tags and attributes, and behavior-bearing configuration. Exclude tests, generated output, documentation, blank and comment-only lines, whitespace-only edits and lines containing only structural delimiters (e.g. `)}`). Record additions, deletions and exclusions. Count ambiguous production lines. Keep changed tests available for verification.

At 60 lines the round qualifies. At 61 or more, or if the count cannot be established from the available diff, use the ordinary review-fix delta and state why. A first review uses the ordinary depth. If the prior review or either revision is missing, identify the missing input before claiming a delta result. A small final push does not reset the round's count.

## Check the delta

1. **Prior findings.** For each outstanding ID, reproduce or trace its original failure on the new head. Check the other side of the decision the fix changed. If render and an effect both decide freshness, trace a boundary crossed between their clock reads. Record fixed, still open, or unverified with a test/assertion or code location. Keep an open ID and its actual severity. A partial fix must name the residual scenario.
2. **Accessibility and permissions.** On touched paths, trace affected keyboard, focus and announcement behavior across success, failure and recovery. For async focus changes, record who had focus at activation and at completion, including pointer activation. If multiple live regions change, identify which ones announce the same outcome. For a changed access or data boundary, check allowed and denied users or resources through enforcement and what is returned or displayed. Record the evidence for each dimension, or why the delta does not touch it. Distinguish DOM facts from observed assistive-technology behavior.
3. **Claimed mutants.** Map each mutation claimed for this revision to its test and the assertion that should fail. Check the clean revision and the named mutation using revision-matched execution evidence or a targeted run in disposable scratch. Distinguish killed by the intended assertion, survived, and unverified. Record a missing list, unavailable runner, or source-only prediction as unverified. Never replace an unspecified campaign with invented mutants or infer kills from a green suite.

Verify incidental observations encountered during these checks. Report at most three additional P3 findings for the entire round, in rank order, without searching to fill the quota. Prior findings and new failures of the three required checks keep their actual priorities and do not consume these slots. If incidental evidence establishes a P0–P2 issue, preserve the evidence and switch to the ordinary delta at its real severity.

## Return the result

Give the revisions, logic-line count, verification mode, prior-ID outcomes, accessibility and permissions results, claimed mutant results, new findings, limits and verdict. Use normal CR IDs and verification verdicts for findings. Apply APPROVE, COMMENT or REQUEST_CHANGES to this delta only. A material unverified claim precludes approval. A presentation cap can shorten the findings display, but the closure and required-check outcomes stay visible. For `findings_file=PATH`, save this report with the same three-extra limit and use the normal file handoff. For structured output see the [report contract](report-contract.md).
