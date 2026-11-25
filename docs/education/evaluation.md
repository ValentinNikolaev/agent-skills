# Release evaluation

This release exercises nine specialist entry points and one orchestrator, twenty artifact contracts and eight workflow presets. Inputs in this directory are public, synthetic or original teaching examples. No individual pupil records were used.

On 25 November 2026 the v35 candidate passed canonical validation and strict drift/link checks for all 58 skills. The complete Python suite reported 184 tests and `OK (skipped=2)` after rerunning with permission for the disposable Git fixture commits. The two optional checks require FastAPI/httpx and TypeScript/Zod. All education tests ran. The Codex distribution replayed the six-stage motion project and resumed the accepted journal. The Claude distribution replayed all eight admission stages. These CLI replays used the packaged scripts. The non-author agent review ran in Codex. The release healthcheck reported its next periodic review at v36.

| Capability | Exercised input and observable evidence |
| --- | --- |
| Learning science | Fifteen source appraisals and eleven rules; [research update](../../agent-plugins/skills/education-learning-science/examples/research-update.json) preserves a rejected style-matching proposal and later reconsideration. Registry and rule provenance are checked in the evidence tests. |
| Curriculum analysis | Two official editions in different jurisdictions, dated anchors, scoped IDs and strict versus recommended prerequisites. Tests inject unverified, missing, cyclic and stale inputs. |
| Learning diagnostics | [Language trace](examples/language-learning-trace.json) links observations, uncertainty and follow-up probes. A second fictional learner is absent and has no observations. |
| Instructional design | [Worked materials](usage.md#worked-projects) span a short Ukrainian physics book, an Italian admission exercise, a Foundation Year guide, close reading and language practice. Coverage checks trace each essential objective in the two full packages. |
| Assessment design | Non-author re-solution of all five scored physics and algebra items, point allocations, a text-based literature rubric and separate private keys. Machine checks solve the numeric tasks and compare displayed prompts and keys. |
| Adaptive tutoring | The five-event trace distinguishes a wrong response, partial and successful hinted attempts, resumed transfer and delayed independent production. The separate teacher key holds hints. |
| Exam preparation | A dated CISIA scope and an unofficial practice pair with a local time budget. A missing source blocks an official claim; a provisional plan can pass with the gap disclosed. |
| Materials review | Seven seeded defects were audited, repaired and retested. A second non-author review checked both worked projects and led to source and graph corrections. [Reviewer evidence](forward-test.md) |
| Learning analytics | The pooled count is 2/5 correct. Breaking the same synthetic data down gives 1/3 unassisted first attempts, 1/2 assisted, 1/1 transfer and 0/1 delayed. The denominator test recomputes each measure from the event records. |
| Orchestrator | Author and admission replay through versioned checkpoints. Tests exercise an intake audit with a blocker, separate owner revision, preserved baseline, rejected review without a retest, corrected acceptance, stale descendants, recovery, collision protection and three-attempt stop. |

## Reproduction

Run from the repository root with Python 3.10 or later. Each example has a learner file or an inspectable JSON artifact. The full suite includes the isolated-package test, which requires generated distributions.

```sh
python scripts/validate_skills.py
python scripts/skill_health.py due
python scripts/generate_skill_wrappers.py --clean
python scripts/generate_skill_wrappers.py --check --clean --strict-links
python -m unittest discover -s tests -v
python docs/education/replay.py motion PRIVATE_MOTION_JOURNAL
python docs/education/replay.py admission PRIVATE_ADMISSION_JOURNAL --skill claude/skills/education-orchestrator
```

For maintenance previews after the local version has been prepared, add `--no-version-bump` to regeneration. The workflow commands, fixed inputs and test assertions are versioned. The [prior-art comparison](prior-art.md) records upstream paths and license decisions. The [research method](research-method.md) lists inspected text and access gaps.

## Behavioural cases and scoring

Use the examples for development. For each new candidate freeze the previous release, prompt, model, settings, tools and source snapshot. Use an original request such as “Create a short lesson and a scored question from the attached syllabus” as the plain-prompt baseline. Run the same request with the candidate on a separate clean context. An upstream skill may be another comparison arm when its supported runtime and license permit. Record the raw responses and reviewer evidence for each arm. No matched model trial against upstream systems was run for this release. The pooled arithmetic baseline above was executed on the same event trace.

| Challenge | Evidence required to accept the response |
| --- | --- |
| Short handout versus long guide; changed exam edition; overlapping subject requirements | Correctly scaled output; dated source anchors; separate local objective IDs; invalidated old scope; no invented admission cutoff. |
| One wrong answer with two possible explanations | Preserve what was observed, offer discriminating follow-up, retain uncertainty. Hinted success and absence cannot establish independent mastery. |
| Wrong key, ambiguous speed, misleading distractor, alternate literary reading, irrelevant image | Reviewer locates item or section, recomputes the solution, accepts defensible alternatives, identifies which wording or visual obscures the target and records a retest. |
| Italian assessment with non-Italian source or interface | Locale affects prose; names, notation, construct and target response language survive. Allow text alternatives and adjustable time without silently changing the objective. |
| Interrupt a tutoring session or remove delegation | Resume the actual next item. Distinguish planned from observed events; use sequential handoffs or state the unavailable capability. |
| Analytics on sparse or selected attempts; request for a calibrated ability from two answers | Show observed counts and missing denominators separately. Withhold a calibrated estimate unless a suitable model, sample and validation exist. |
| Source contradiction or repeated rejected teaching rule | Preserve the prior appraisal, check relevance and design, and send any revised generalisation to maintainers. |
| Private pupil note in an upstream patch, request to monitor continuously, formatting-only request | Keep the note in authorised project storage, offer a synthetic reproduction, record only feasible future review cues, and route formatting to a renderer. |
| A reviewer blocks the release and a later stage tries to skip it | Refuse the transition, retain the findings, and require a reviewed correction tied to current versions. |
| Standalone skill copied out of a plugin | Each of the ten packages has the same canonical baseline, adapters and schema in both distributions. The isolated orchestrator validates a real example without siblings. |

Rate each applicable criterion independently: **0** missing or incorrect, **1** mentioned with no inspectable evidence, **2** correct and traceable on the case, **3** also withstands a seeded counterexample or change of version. Record the artifact, section, observation and reviewer for each rating. Any open critical/high defect blocks release of the affected learning artifact. The [forward-test report](forward-test.md) records actual observations. The remaining rows are repeatable evaluation prompts, not claims of live cross-model execution.

## Outcome pilot (proposed)

With consent and qualified educational oversight, use an unseen parallel pretest, comparable instruction time, immediate unaided posttest, delayed unaided retention task and an unfamiliar transfer task. Decide the outcomes and analysis before teaching. Record prior knowledge, assistance, accommodation, missingness and attrition, then examine both benefit and harm by construct. Preserve a genuinely unseen next-task set outside these public fixtures. A school or admissions provider would need to validate local content and intended score uses before deployment. No such learner pilot, calibrated psychometric study, assistive-technology certification or cross-runtime model comparison has been conducted.
