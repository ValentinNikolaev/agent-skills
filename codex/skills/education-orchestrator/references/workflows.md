# Routing and gates

| Specialist | Send | Accept |
| --- | --- | --- |
| Learning science | Population, teaching decision, counterexample | Source/rule IDs, applicability and limits |
| Curriculum analysis | Official edition or explicitly provisional scope | Anchored requirements, concept graph and gaps |
| Diagnostics | Goals, permitted observations and level of assistance | Alternatives to each diagnosis, uncertainty and follow-up probe |
| Instructional design | Audience, requirements and assessment intent | Observable objectives, sequence, editable lessons, guided and independent practice |
| Assessment design | Objectives, purpose, constraints | Blueprint, items, private solutions, scoring and independent answer check |
| Adaptive tutoring | Profile or starting probe, goals and available time | Actual responses, hints, next task and resumable schedule |
| Exam preparation | Dated specification and budget | Gap priorities, timed practice and bounded readiness statement |
| Materials review | Frozen artifact versions, purpose and criteria | Located findings, owners, retest evidence, decision and independence |
| Learning analytics | Authorised events, question and window | Denominators, missing cases, assistance and transfer separated, proposed action |

Presets in [presets.json](presets.json) define dependencies and accepted output types. Use **author** for a guide or textbook. The blueprint releases chapter drafting and item writing to run independently. Include science appraisal only for a new teaching claim, and diagnostic intake only for personalisation. **Admission** adds diagnosis and exam planning. A group with no observations can receive an explicitly empty baseline and a first diagnostic probe. Add tutor and interpretation stages only when interaction is requested. **Repair** starts with an audit that may find blockers, routes by actual defect owner (replace the default material-revision node for scoring or curriculum defects), then retests. **Tutor** records observations and updates a schedule. Add a new assessment stage if no suitable task exists. **Map** ends with the graph unless the stakes warrant review. **Assess** starts with validated external objectives and ends with independent item review. **Research** records a proposal and its evaluation for a maintainer. **Outcomes** accepts authorised observations and ends with recommendations. Turn an approved recommendation into a new project revision.

For an ad hoc DAG copy only needed node specifications. Record the reason for omitted optional branches in the brief. Scope changes get a new brief revision and a new plan that reuses only artifacts whose dependencies still hold. Put alternate providers or parallel agents behind the same handoff. Dependency edges schedule work. Artifact references record what a producer actually used. A defect report points at the old revision. Its replacement gets a new revision, retaining history in project storage.

| Gate and owner | Blocking evidence | Advisory or provisional handling |
| --- | --- | --- |
| Intake and privacy, coordinator | Unauthorised processing, missing essential input for a personalised claim | Minimise data, use a generic audience or request a probe |
| Scope and evidence, curriculum/science | Fabricated source or essential objective without authority | Unavailable edition allows explicitly provisional practice only |
| Instruction, design | An essential objective lacks teaching or a prerequisite | Adjust time estimate after learner feedback |
| Scoring, assessment | Wrong key, material ambiguity, invalid rubric or missing essential assessment | Difficulty estimates remain provisional until observed |
| Usability and fairness, reviewer | Serious barrier to the intended task, unsafe content or changed construct | Record untested assistive technology or alternate format |
| Delivery, coordinator | Open high/critical finding, stale target, or missing human approval for high-stakes use | Share a labelled non-release draft with the unresolved gate |

Do not claim that a stored schedule will fire a reminder. Record the next review cue for the next invocation. Keep the private event bundle and public teaching package in separate directories. Share only the specific artifacts authorised for the recipient.
