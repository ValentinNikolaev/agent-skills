# Evaluator key

Freeze the contracts, patches, key and reviewer configuration before obtaining the first answer. Use a fresh, tool-free session per packet. Give each session the applicable pinned skill text, one contract and one full-context patch. Keep this file, the other versions, grader and run outputs outside reviewer input.

| Packet | Evidence required for credit |
|---|---|
| K7 | Opening 403 leaves the view blank, retains the record and requests a fresh check. Opening 503 retains the record and permits retry. After display the same 403 wrongly schedules a fresh check, leaves the old value visible and leaves its cache entry in place. Both post-display effects and the distinguishing signal (operation or phase) must be explicit for a full hit. A blanket classification of 403 as terminal fails. |
| R2 | Same contract. Opening 403 and 503 take distinct recovery paths. The watch 403 hides the value and evicts only its key. Watch 503 preserves the displayed value and permits retry. Count each unsupported actionable finding as a false positive. Record coverage limits separately. |
| M4 | Empty input is fixed. A nonempty final partial batch is dropped. Credit a concrete counterexample and consequence. Count any cache, authorization or phase finding as a false positive. |

Score each branch as explicit, partial or absent. Credit an unchanged branch only if the reviewer traces it. Separate genuine findings, unsupported findings, and missing verification. Record the CLI input, cached input (a subset), and output tokens separately for each case. The unit of observation is one first answer per case.

If K7 is fully detected and R2 has zero false positives, propose the three fixtures as a regression set and stop. If the phase distinction is missed, insert one sentence beside the classification rule in an experimental copy and rerun the same packets in fresh sessions with the same model, effort, format and budget. Compare the first answers; do not tune against repeated runs.
