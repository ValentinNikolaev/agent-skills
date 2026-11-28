# Regression candidate for ordinary review-fix deltas

Keep the defective patch, its clean sibling and an unrelated arithmetic fix as a blinded set. The published skill identified the phase-specific failure and raised zero findings on the clean sibling. The defective-case report gave weaker evidence for the outage branch. The results support keeping that branch in the grading key. They give no reason to extend the skill on the basis of this run.

## Materials and procedure

The canonical source was `ValentinNikolaev/agent-skills` at `79dee507d8a7c8c432edc4f949780dbd9d6c5ba2`, verified against GitHub master. Local pending changes were excluded. [Classification boundaries and Review-fix deltas](../../../agent-plugins/skills/code-review/references/conditional-checks.md#classification-boundaries) already require checking the discriminating signal, both outcomes and the opposite side of the fix.

| Case | Evidence given to its reviewer | First answer used for grading |
|---|---|---|
| K7 | [Panel contract](panel-contract.md), [patch](K7.diff) | [CLI record](K7.json) |
| R2 | [Panel contract](panel-contract.md), [patch](R2.diff) | [Recovered answer](R2-first.txt) |
| M4 | [Export contract](batches-contract.md), [patch](M4.diff) | [Recovered answer](M4-first.txt) |

Each synthetic patch is the whole change from a previously reviewed one-file revision, with both call sites visible where applicable. Each model session received the pinned skill, relevant reference material, one contract including the earlier review finding, and one diff. The sessions could not read each other's inputs or answers. The [grader](grading.md) and packet hashes were [frozen](lock.json) before review. The reviewer had no tools. The evaluator separately applied and executed the patches in scratch.

All sessions used GPT-6 Sol at medium effort, quick depth on an ordinary fix round, compact format, one turn, a requested 650-word report, a configured 32,768-token context window and a 300-second timeout. Verification within each review was inline. This tests the supplied contract and the pinned skill together. There was no no-skill arm.

## First-answer grades

| Branch | K7 | R2 |
|---|---|---|
| Opening 403 | Distinguishes the expired receipt, fresh check and retained cache. Blank view implicit. | Explicit blank view, retained entry and fresh check. |
| Opening 503 | Mentions tracing 503. Retry and resulting state are undocumented. | Explicit retry with view and cache preserved. |
| Watch 403 after display | Confirmed P1. Both callers reach the shared helper. It queues a fresh check and leaves both the old display and cache entry intact. Remediation covers hiding, targeted eviction and closure. | Explicit clearing, selected-entry eviction and closure. No finding. |
| Watch 503 | Mentions 503 without describing the outcome for this phase. | Explicit retry with view and cache preserved. |
| 200 | Mentions tracing 200 without explaining either outcome. | Mentions tracing 200 without explaining either outcome. |

K7 received `REQUEST_CHANGES`. R2 received `COMMENT` solely for unavailable dispatcher and test evidence. It had **zero actionable findings**. M4 received `REQUEST_CHANGES`. It correctly traced five items at capacity four to one allocated batch instead of two. Empty input and exact multiples worked. It made no cache or authorization claim. Its coverage description alternated between unknown and uncovered in the supplied evidence. The executable test coverage in the hypothetical project is unknown.

The evaluator checked each panel status in both phases, including preservation of a second cache key. On the common base, only opening 403 failed. K7 moved that failure to watch 403. R2 passed all six cases. M4 fixed the empty case but failed for one and five items at capacity four. Reproduce these checks from the repository root with `python -B docs/experiments/classification-phases/check_fixtures.py`.

## Measured context

| Packet | Supplied bytes (UTF-8) | CLI input tokens | Of which cached | Output tokens |
|---|---:|---:|---:|---:|
| K7 | 72,429 | 112,558 | 94,464 | 1,311 |
| R2 | 72,656 | 111,918 | 93,952 | 1,574 |
| M4 | 63,662 | 104,249 | 82,176 | 880 |

Bytes cover the complete supplied prompt. The token columns are CLI turn totals, including host overhead and repeated context. They do not measure peak occupancy. Cached tokens are included in input. K7 has first-answer usage. For R2 and M4 the initial collector rejected a CLI notice before saving usage. The original review text was recovered from console output with some punctuation loss. The [R2](R2.json) and [M4](M4.json) telemetry comes from fresh runs with the same packet hashes and settings. They confirmed the finding counts. R2's repeat returned `APPROVE` for the supplied scope. The grading table uses its original verdict. Published response records omit session identifiers and host-clock annotations. Temporary host directories in answers are anonymized.

The condition for testing a rule amendment was a missed phase distinction. K7 identified it, and R2 produced no false positive. There is consequently no amended-skill result. For future skill revisions, rerun each packet independently and compare branch evidence, control findings and usage with this baseline. The set distinguishes both a reviewer that misses post-display revocation and one that recommends clearing the cache on every 403.
