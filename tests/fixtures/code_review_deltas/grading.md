# Grading ordinary code-review fix rounds

Give the reviewer the contract (`context_file`) and diff (`patch`) named in `../review_failure_controls.json`. Use a fresh session for each case. Keep the case registry, this key, the other packets and the executable checks with the evaluator.

## Panel cases K7 and R2

Score each row separately in **both** reviews. Start with the selected record and a second, unrelated entry in the cache. For a watch response, first open the selected record successfully so its value is already visible.

| Response | Expected screen | Expected cache | Expected next action |
|---|---|---|---|
| Opening 403, receipt expired | Blank | Both entries retain their original values | Request a fresh permission check before display |
| Opening 503, receipt checker unavailable | Remains blank | Both entries retain their original values | Retry the opening receipt check |
| Watch 403, access removal confirmed | Previously displayed value is hidden | Evict the selected entry only. Preserve the unrelated entry and its value | Close the panel and stop the watch |
| Watch 503, permission watch unavailable | Previously displayed value stays visible | Both entries retain their original values | Retry the permission watch |

For each 503, award full credit when the review traces the affected operation and states the screen, cache and retry outcome. Award partial credit when it explains only some of these effects. Mark a bare mention of tracing 503, or a correct trace for only the other phase, as missing evidence for that row. Grade omissions separately from false findings.

For **K7**, require the reviewer to distinguish the two sources of 403 and identify the actual watch failure. The new helper schedules a fresh check, leaves the old value on screen and keeps its cache entry. A fix must preserve opening recovery and both outage paths. For **R2**, all four rows conform. Count each unsupported actionable finding as a false positive. A stated verification limit alone earns no false positive.

## Export case M4

Credit the review for identifying that the fix handles an empty export but drops a final partial batch. Require a concrete input and consequence. With five items and capacity four, the new expression allocates one batch and the export needs two. An exact multiple, such as four items at capacity four, still fits. Count any cache or authorization finding on this patch as a false positive.
