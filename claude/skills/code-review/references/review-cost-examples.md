# Review handoff and model examples

These examples illustrate invocation conventions, not new helper CLI flags. Delta trigger, batching, exclusion, and scope examples live with [review-fix deltas](conditional-checks.md#review-fix-deltas).

| Request or condition | Before | After |
|---|---|---|
| Review PR 801 round 2 and pass findings to its author session | Paste the complete report between sessions; a lost message requires another explanation | Invoke with `findings_file=_coord/DEV-36918/review-backend-801-r2.md`; save the complete report once and forward the path plus severity counts and a line for every retained finding |
| File handoff with `--max-findings 0 --format compact` finds a P1 and a P2 | The display cap can leave a handoff with no actionable detail | Artifact contains both full CR blocks, evidence, coverage, limits, revisions, and verdict; return the path, `P0=0 P1=1 P2=1 P3=0`, and both finding lines below |
| File handoff contains only a P2 accessibility finding and a P3 UI finding | Return no actionable lines because neither blocks merge | Return both lines with ID, priority, category, location, and scenario; the full file retains their evidence |
| No output path supplied | Full or compact report in chat | Same report contract; no file is created |
| Requested output path is unwritable or already belongs to an unrelated report | Return a path before confirming that the artifact exists, or overwrite prior work | Report the write failure/collision; preserve existing content and do not claim a successful handoff |
| A delegated Go reviewer has an Agent tool and needs independent verification | Spawn a nested checker that repeats the review workflow | Return candidates and verification needs to the top-level coordinator, which can assign a direct sibling verifier |
| Dependency loading requests missing checksum entries | Run `go get`, plain `go mod tidy`, or `-mod=mod` in the checkout and cite the resulting `go.sum` lines | Use `go mod tidy -diff` or a scratch `-modfile` and matching `.sum`; cite original reviewed lines and label proposed dependency changes as check output |
| A check unexpectedly changes a file that was already dirty | Reset the file, or report transient lines as part of the PR | Stop the check, disclose the write, preserve concurrent work, and verify evidence against the original revision or captured input |
| A standard review changes 1594 production/other lines and 762 test-only lines with three available subagent slots | Treat 2356 raw lines as sixteen mandatory finder passes and always report a deficit | Weight tests at 0.25: `W = 1784.5`, advisory `D = 3`; reserve one verifier and plan three finder partitions including the coordinator, with all changed tests still inspected |
| A production-heavy review's advisory demand exceeds available finder roles | Spawn more agents or report a quota deficit despite complete partition coverage | Record the capped plan and budget saturation; report a deficit only for an unfinished partition or a named omitted check, and extend sequentially only when actual coverage needs it |
| UI layout, documentation, or wording diff with no concurrency/storage logic | Caller defaults every review to its most expensive model | Caller can choose a cheaper model such as Sonnet; review depth and evidence rules still apply |
| Fix changes retry ownership or cleanup of concurrent storage writers | Caller uses the UI-review model merely because the diff is small | Recommend the top model; the skill itself never changes the model |

Successful short response for the example with one P1 and one P2:

```text
_coord/DEV-36918/review-backend-801-r2.md
P0=0 P1=1 P2=1 P3=0
CR-001 | P1 | reliability | worker.go:83 | retry after commit can publish the same event twice
CR-002 | P2 | ux | Form.tsx:42 | invalid input disables Save without visible feedback
```

The file retains the existing finding fields, including `Failure scenario` and `Verdict: CONFIRMED | PLAUSIBLE`, and the merge verdict. Counts describe all retained findings before a display cap. A zero-finding file still records scope, evidence, coverage, limits, and verdict; return its path and four zero counts, without finding lines. Reading a path alone is not evidence that a review completed: the receiving session reads the artifact's revisions and verdict.

Routing examples: an existing diff with `findings_file=...` activates `code-review`; a request to apply the findings activates `fix-pr`; an ordered proposal without a diff activates `plan-review`. File output authorizes only the requested report, not source edits or posting GitHub comments.
