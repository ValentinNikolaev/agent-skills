# Forward test of education material review and repair routing

Run on 2026-11-25 in the Codex task's independent subagent. The evaluator read the new canonical `education-materials-review/SKILL.md` and `education-orchestrator/SKILL.md` and authored a synthetic flawed handout in an isolated temporary directory. The evaluator was separate from the agents who wrote those skills. Since the evaluator also made the fixture and its repair, defect detection was not blind and the revised content did not receive an independent second reviewer. The result tests instruction use and arithmetic. It does not measure learner outcomes or empirically validate the skills.

## Exact input

The initial file was `motion-v1.md` in an isolated temporary project. Its complete text was as follows.

```markdown
# Motion lesson and scored check
Version 1. Target group is 12-year-old learners. Source language is English. Instruction is in English.

Objective O-M1. Calculate average speed with consistent units.
Objective O-M2. Distinguish distance travelled from displacement on a straight route.

The Ministry Science Standard 2026 section 7.3 requires every learner to draw a velocity-time graph at this grade. This is our official alignment.

Speed is found by multiplying distance by time. A car travels 12 km in 2 hours, so 12 × 2 = 24 km/h.

Diagram D1 is essential. Look at the diagram above to decide which direction the student travelled. [No diagram or text equivalent is supplied.]

Item Q1, worth 1 mark. A runner covers 10 m in 2 s. What is the average speed?
A. 5 m/s
B. 20 m/s
C. 12 m/s
Key Q1. B.

Item Q2, worth 1 mark. A learner walks 3 m east and then 3 m west. How far did the learner move?
A. 0 m
B. 6 m
Key Q2. B.

Rubric. Award 1 mark for either item only when the response matches the key. Total marks 3.
```

The review instruction was to inspect this artifact for factual accuracy, objective coverage, source fidelity, ambiguity, answer keys, scoring, accessibility and release status. The evaluator used the materials-review procedure and the repair preset routing guide, then saved the report as `review-v1.md` in the same temporary directory.

## Observed review and repair

The review produced seven located findings and a blocking decision.

| Finding | Severity | Observed evidence | Routed owner |
| --- | --- | --- | --- |
| F1 | Critical | Average speed is distance divided by elapsed time. The worked value is 6 km/h, while the lesson teaches multiplication and gives 24 km/h. | Instructional design |
| F2 | Critical | Q1 computes to 5 m/s. Its key selects 20 m/s. | Assessment design |
| F3 | High | Q2 permits 6 m of travel and 0 m of displacement. The stem does not identify the construct. | Assessment design |
| F4 | Critical | The claimed official standard lacks a jurisdiction, issuer URL, edition and verifiable section anchor. | Curriculum analysis |
| F5 | High | The essential diagram and text equivalent are absent. | Instructional design |
| F6 | High | O-M2 is tested before any explanation of distance versus displacement. | Instructional design |
| F7 | Medium | The two one-mark items conflict with a stated total of three marks. | Assessment design |

The evaluator checked motion definitions against [OpenStax College Physics 2e, section 2.1](https://openstax.org/books/college-physics-2e/pages/2-1-displacement) and [section 2.3](https://openstax.org/books/college-physics-2e/pages/2-3-time-velocity-and-speed). The official claim was left unverified and removed during repair. The corrected learner file was saved as `motion-v2-learner.md`. Its complete text was as follows.

```markdown
# Motion lesson and practice
Version 2. Target group is 12-year-old learners. Instruction and assessment language are English. This is a generic teaching example. Curriculum alignment is provisional because no jurisdiction, edition or official source was supplied.

Objective O-M1. Calculate average speed from distance and time in consistent units.
Objective O-M2. Distinguish total distance travelled from signed displacement on a straight route.

Distance is the length of the whole route. Displacement is the change from the starting position to the ending position, including direction. Walking 3 m east then 3 m west covers 6 m of distance and gives 0 m displacement because the ending position is the starting position.

Average speed = total distance / elapsed time. A car travels 12 km in 2 hours. Its average speed is 12 / 2 = 6 km/h. Both quantities use compatible km and hours.

Guided check. A cyclist covers 8 km in 2 hours. Divide 8 by 2 and explain the resulting unit.

Independent item Q1, worth 1 mark. A runner covers 10 m in 2 s. Calculate average speed in m/s and show the calculation.

Independent item Q2, worth 2 marks. A learner walks 3 m east and then 3 m west along a straight path. State the total distance and the signed displacement. Explain the difference using the start and end positions.

Transfer prompt. A learner walks 4 m west and then 1 m east. Work out total distance and signed displacement. Decide whether average speed and average velocity could have the same magnitude on this route, and explain why.
```

The teacher file `motion-v2-teacher.md` kept solutions and marking guidance apart from the learner text. It stated 4 km/h for the guided check, 5 m/s for Q1, 6 m travelled and 0 m displacement for Q2, and 5 m travelled with 3 m west displacement for the transfer prompt. The two scored items totalled three marks. It stated that alignment to an official syllabus remained provisional.

The second review read both revised files and recorded F1–F7 as repaired. It confirmed that the essential objective has an explanation before independent practice, that the Q2 stem asks for two distinct quantities, and that the learner handout contains no answer key. The review passed the generic draft with its provisional alignment label. No official age or curriculum mapping, learner trial, or assistive-technology test was conducted.

## Runtime observations and reproduction

The following commands ran against the canonical working-tree scripts. `workflow.py init` created `checkpoint-00000000.json` for the repair preset. `status` showed `audit ready`, with `revise` and `review` pending. Starting the audit and recording a block created checkpoints 1 and 2. The final status showed `audit blocked` and both downstream stages pending. This demonstrates a real stop on a critical review finding. The replay did not accept typed `LearningMaterial`, `AssessmentItem` and `ReviewReport` artifacts through the contract validator, so it does not demonstrate an automated repair transition or downstream invalidation.

```text
python agent-plugins/skills/education-orchestrator/scripts/workflow.py init <temp>/journal --preset repair --project motion-review
python agent-plugins/skills/education-orchestrator/scripts/workflow.py status <temp>/journal
python agent-plugins/skills/education-orchestrator/scripts/workflow.py start <temp>/journal audit
python agent-plugins/skills/education-orchestrator/scripts/workflow.py block <temp>/journal audit --reason 'Critical subject and scoring defects in review-motion-1'
python agent-plugins/skills/education-orchestrator/scripts/workflow.py status <temp>/journal
python -c "assert 12/2==6 and 10/2==5 and 8/2==4 and 3+3==6 and 3-3==0 and 4+1==5 and -4+1==-3; print('physics arithmetic checks passed')"
```

The arithmetic command printed `physics arithmetic checks passed`. The isolated review directory holds the complete v1 and v2 files and review notes for this local run. Only this report is part of the repository. The repair preset's static `revise` node assigns instructional design. Its guide explicitly requires replacing that node for scoring or curriculum defects, which this case has. A subsequent integration test should exercise that custom multi-owner plan with typed artifacts and a checkpoint resume.

## Independent review of the worked projects

On 2026-11-25 a subagent who had not authored the worked projects read `docs/education/examples/motion/{project.json,learner.md,teacher.md}` and `docs/education/examples/admission/{project.json,learner.md,teacher.md}`. This pass inspected all five final scored items, the worked examples, the selected official scope, the learner/teacher separation and each bundle's objective links. It did not observe real learners or a qualified school or examination specialist. The two official sources were opened at their linked URLs during this pass.

| Project | Independent subject and scoring result | Official-scope result | Finding or limit |
| --- | --- | --- | --- |
| Motion | The reversal item gives 8 + (8 − 3) = 13 m of travel and +3 m displacement. The uniform-motion item gives 18 / 6 × 4 = 12 m. The returned-to-start explanation gives zero displacement and positive distance. The worked 12 / 4 = 3 m/s and next-two-seconds distance of 6 m are correct. | The Ukrainian ministry's 2024 model programme names grade 7 mechanical motion, path, displacement, speed, units, and movement calculations in topic 2 on printed pages 20–21. The example expressly claims only a selected slice and does not claim a particular school's adoption. | The first read found a strict speed prerequisite through a combined `distance and displacement` node. That node was split into path length and signed displacement, and speed now depends strictly on path length and elapsed time. The first read also found restrictive reuse terms on the linked OpenStax page. The project replaced that source with a NASA manual. A second read caught an incorrect NASA page anchor. The final record and teacher note now point to Session 1, printed page 1.6, where the average-speed definition appears. |
| Admission | The model equation factors as (x − 3)(x + 2), yielding 3 and −2. The two scored equations factor as (x − 2)(x − 3) and (x + 4)(x − 3). Their keys 2 and 3, then (−4, 0) and (3, 0), are correct. The prompts, keys and lesson sections in the bundle exactly match the learner and teacher files. | The CISIA 2026 TOLC-I syllabus explicitly includes second-degree algebraic equations, factorisation, equations of parabolas and graphs of elementary functions. CISIA's current structure page says the mathematics section has 20 questions in 50 minutes. The pack says its two open-response tasks and local rubrics are unofficial and limits its scope to two objectives. | The syllabus names parabola equations and graphs, while the project turns x-intercept interpretation into a local objective. Its `req-2` wording should be read as a selected interpretation of that official topic, not a verbatim requirement. Candidate readiness and university admission conditions remain unknown. |

The independent reviewer also checked that each final item prompt appears in its learner file, each exact key appears in its teacher file, and every `LearningMaterial` body and practice field appears in the learner file. Both bundles passed `workflow.py check --alignment`, yielding 13 and 15 validated artifact revisions respectively. These checks establish contract shape and traceability within the samples. The arithmetic and source reading establish the sampled subject findings. They do not prove instructional effectiveness or full syllabus coverage. The [NASA manual](https://www.nasa.gov/wp-content/uploads/2014/10/563411main_ftnl_student_manual.pdf) gives the average-speed definition in Session 1, printed page 1.6. [Ukrainian ministry model programme](https://mon.gov.ua/static-objects/mon/sites/1/zagalna%20serednya/Navchalni.prohramy/2024/Model.navch.prohr.5-9.klas-2024/31-12-2024/fizyka-7-9-kl-kreminskyy-ta-in-31-12-2024.pdf), [CISIA 2026 syllabus](https://www.cisiaonline.it/sites/default/files/Sillabi/2026/Syllabus-TOLC-I-2026.pdf), [CISIA structure](https://cisiaonline.it/en/tolc/tolc-i/structure-and-syllabus).

After the motion corrections, the reviewer reopened `project.json` and `teacher.md`, confirmed the revised graph edges and source anchor, and reran both alignment commands. The motion bundle still validated 13 artifact revisions, and the admission bundle validated 15. No unresolved critical or high content finding remained in these two inspected examples. After the independent pass the author narrowed the admission `req-2` wording to CISIA's listed coordinates and loci. The intercept exercise remains a locally chosen objective.

```text
python agent-plugins/skills/education-orchestrator/scripts/workflow.py check docs/education/examples/motion/project.json --alignment
python agent-plugins/skills/education-orchestrator/scripts/workflow.py check docs/education/examples/admission/project.json --alignment
```
