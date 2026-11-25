---
name: education-orchestrator
description: Coordinate multi-stage education projects, specialist handoffs, review and resumption of versioned materials.
---

# Education orchestrator

Start with the deliverable. A teacher asking for a replacement rubric needs assessment design. A department replacing a workbook, its rubric and its timed practice needs a coordinated project. Answer ordinary homework questions directly. Send translation or PDF-only requests to the available language or rendering tool.

1. Establish intended audience and use, subject and scope, available time, stakes, authorised source material and the separate languages for interface, instruction, assessment and sources. Set aside identifying learner details. Open the latest project checkpoint if it exists. A generic course needs an audience brief only. A personalised course with insufficient responses needs a diagnostic probe or a provisional plan.
2. Match deliverables to owners in the [workflow guide](references/workflows.md). Honour named specialists and limit work to the requested scope. Select the smallest preset or supply a DAG for the actual situation. List inputs, acceptance checks and owners of unresolved decisions. Reuse accepted outputs only for the same scope, revision and dependencies.
3. Discover each specialist in the installed catalogue. Read its own instructions. Pass one handoff per stage with task ID, intent, constraints, input IDs and revisions, required contracts, applicable rule IDs, permitted writes and acceptance tests. Request status, produced IDs and revisions, warnings and next action in return. When an authorised agent interface exists, independent stages can run separately. With a single agent, execute roles in dependency order and record that fact. Missing a specialist? Use its available portable instructions or request the missing deliverable and block dependants. Do not count a proposed call as execution.
4. Run gates against the returned content. Check sources, objective coverage, subject accuracy, key and scoring, accessibility, privacy and independence in proportion to the task. A passing structural check alone cannot certify an answer key or an official claim. The material author may correct their own work. An independent reviewer checks the new revision or records the limits of a separate reading. A qualified human must approve high-stakes use. Record review scope and actual reviewer status.
5. Save each accepted revision and its dependencies outside the skill. Use the [checkpoint tool](scripts/workflow.py) with the [command guide](references/checkpoints.md), or follow the same statuses on paper. On a rejection, preserve the report, route fixes to the producer, invalidate dependent artifacts and retest only that branch. Stop at the retry limit or an unmet critical gate and deliver the labelled draft with its outstanding owner and evidence. Ask before a consequential change of scope, external action or disclosure.
6. Deliver editable learner materials separately from keys, teacher instructions, private diagnostic records and process history. For a requested PDF, slide deck or document, hand the reviewed source to the appropriate renderer and inspect its output when available. State exactly what was verified and which official or human decisions remain open.

**Direct example.** “Resume this physics workbook after its answer key was corrected.” Read the latest manifest, reopen the item stage for the replacement revision, recheck any dependent review and return the corrected learner and teacher files.

**Offline example.** For a two-week algebra course, use the bundled registry and supplied syllabus. Mark exam alignment provisional when the current specification cannot be verified. Run the author preset sequentially. A request for a single misconception probe goes to learning diagnostics.

The installed package includes `references/education/contracts.json`, `evidence.json` and `adapters.json` in that directory. Read only entries needed for the handoff. Local project changes belong in its private workspace. A shared rule change requires a proposal, evidence, regression checks and a maintainer decision.
