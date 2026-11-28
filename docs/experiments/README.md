# Skill experiments

The [code-review fix-round experiment](classification-phases/README.md) compares a permission change before and after displaying a cached record. Its [regression grading key](../../tests/fixtures/code_review_deltas/grading.md) covers both outage paths and the clean control.

The [humanizer pilot](sim-humanizer/README.md) used six synthetic passages. The base and both proposed edits each passed all 18 checks. Its replay instructions and scored texts accompany the report.

## Transfer of edit history

Three rounds tested whether giving a skill editor a history of previous revisions improved its proposed edit. The arms were the existing skill, an edit produced without that history, and an edit produced with it. Each executor answered four tasks twice per arm in each round. A response passed only when all three predeclared criteria passed (`111` in the score files).

| Executor | Skill | Base | Without history | With history |
|---|---|---:|---:|---:|
| Qwen | [audit-docs](journal-transfer/round-01/results.json) | 3/8 | 1/8 | 3/8 |
| Qwen | [prove-checks](journal-transfer/round-02/results.json) | 0/8 | 2/8 | 1/8 |
| Qwen | [verify-impl](journal-transfer/round-03/results.json) | 2/8 | 2/8 | 2/8 |
| GPT-6 Sol | [audit-docs](journal-transfer/sol-replication/round-01/results.json) | 6/8 | 6/8 | 6/8 |
| GPT-6 Sol | [prove-checks](journal-transfer/sol-replication/round-02/results.json) | 8/8 | 8/8 | 8/8 |
| GPT-6 Sol | [verify-impl](journal-transfer/sol-replication/round-03/results.json) | 8/8 | 8/8 | 8/8 |

On fresh GPT-6 Sol tasks, all arms scored 7/8 for [audit-docs](sol-transfer-followup/audit-docs/results.json). For [prove-checks](sol-transfer-followup/prove-checks/results.json), the base and history-free arms scored 4/8 and the history-informed arm scored 8/8 after a [positive control was corrected and rerun](sol-transfer-followup/prove-checks-control/results.json). In the original packet all three arms lacked sufficient evidence to pass that control. The improvement came from two dependency-discovery cases with one pair of authors. The results support testing those cases again with different authors and failure mechanisms.
