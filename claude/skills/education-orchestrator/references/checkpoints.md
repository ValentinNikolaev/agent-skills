# Offline checkpoint commands

Python 3.10+ is optional. The commands run from the installed orchestrator directory. Store the project, its current bundle and the journal in a private project folder outside the plugin. Keep immutable copies of the exact accepted inputs and outputs there. A journal stores IDs, hashes and reason strings. Use pseudonymous project identifiers and avoid personal information in reasons.

```sh
python scripts/workflow.py init JOURNAL --project motion --preset author
python scripts/workflow.py status JOURNAL
python scripts/workflow.py start JOURNAL scope
python scripts/workflow.py check PROJECT.json
python scripts/workflow.py pass JOURNAL scope curriculum@1 graph@1 --bundle PROJECT.json
```

A bundle contains `schema_version: 1`, a list of `sources` (id, title, edition, locator, kind, verification, checked date for verified records) and `artifacts`. Each artifact has `id`, positive `revision`, `kind`, `producer`, `status`, `depends_on` and `data`. Producers are the skill names without the education prefix. Use distinct IDs for multiple items. The bundle is the working snapshot with one current revision per ID. Retain older snapshots separately. The contract dictionary gives field names and types. A plus suffix means one or more entries, an asterisk means zero or more and @ fields require a typed, version-pinned input also declared in depends_on. Source, requirement and rule IDs have their own namespaces. A missing nullable value is written as JSON null. Extensions may add fields; never reinterpret an existing required field within version 1. Refuse unknown versions. Migrate a copy with explicit old-to-new ID mapping, rerun all checks and retain the old snapshot.

Inspect the node's status after interruption. A completed pass writes a new numbered snapshot atomically. An unfinished running stage can be completed in place or reopened with a reason. Start a failed or blocked node only after recording what changed. Three starts per node is this runner's retry budget. Create a newly scoped plan when fresh evidence justifies another attempt. Concurrent writers that race on the same checkpoint get an error; read the latest snapshot before retrying. Choose a local filesystem supporting hard links. On other storage keep a single writer, version the handoff and state files manually, and apply the same transition rules.

```sh
python scripts/workflow.py fail JOURNAL review --reason "Private review rr@1 flags item 2; see saved report."
python scripts/workflow.py reopen JOURNAL items --reason "Replace item 2 key and scoring."
python scripts/workflow.py start JOURNAL items
python scripts/workflow.py pass JOURNAL items item-1@1 item-2@2 item-3@1 --bundle REVISED.json
python scripts/workflow.py refresh JOURNAL --bundle REVISED.json
python scripts/workflow.py check REVISED.json --alignment
```

Check handles partial snapshots as well as whole projects. Alignment requires all essential objectives in the supplied scope to be taught and assessed. Pass requires the direct upstream outputs and their dependencies in the supplied bundle. Refresh expects the complete **current** scope. Omit superseded or unfinished descendants from that snapshot. Changes to an accepted input require a new revision. Refresh marks its producer and descendants stale, including any previously accepted release review. The review must cover the new parent outputs.

In the repair preset, intake-audit freezes the old report in its original snapshot. The revised bundle can now hold the corrected artifact revision. For each blocking intake finding, add a record to the final ReviewReport's optional `retests` list. For example, `{"finding":"audit-report@1#1","target":"guide@2","evidence":"Recomputed the reversed path and read the corrected sign."}` closes the first finding on the old report. Return the final review for the new artifact versions. A missing retest blocks acceptance.

For high-stakes use set the brief's optional `stakes` to `high` and set `high_stakes: true` on the review node in the project plan. The reviewer must include `qualified_approval` with reviewer_role, decision_record and date, tied to the targets reviewed. The tool verifies record presence. The coordinator must check the decision and the reviewer's authority. Unapproved materials can be delivered as a draft. `inventory PROJECT.json` prints material counts without copying personal fields.

Use `init JOURNAL --project NAME --plan CUSTOM.json` for a direct, mixed or revised workflow. A plan is an array of node objects in the format of the bundled presets. Add `"optional": true` only where omission preserves the promised deliverable. Skip requires a reason and cannot bypass a review gate. Block missing official evidence when official alignment is essential. Otherwise accept a provisional artifact with its limits. State is private project history and can be exported or removed with the surrounding project under its retention policy. Nothing runs between calls.

Manual states: pending becomes ready when prerequisites pass or are explicitly skipped. Ready becomes running on dispatch. Running produces passed, failed or blocked with evidence. Only optional unstarted work can be skipped. A changed input reopens a stage and its descendants as stale, which can run again after dependencies are ready. Preserve attempts, old hashes, actual review findings and scope changes in the log.
