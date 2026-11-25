# Using the education skills

For a direct request try “Use education-assessment-design to create two original questions for solving a quadratic over the real numbers. Give the answers and a partial-credit rubric separately.” For a coordinated request try “Use education-orchestrator to turn this syllabus into three lessons, practice and an independently checked key. Teach in Ukrainian, keep the source-language terms, and save a checkpoint after each stage.” Supply a subject and level, and the edition or source files when claiming a particular alignment.

The [workflow guide](../../agent-plugins/skills/education-orchestrator/references/workflows.md) maps all ten owners and eight presets. The [checkpoint guide](../../agent-plugins/skills/education-orchestrator/references/checkpoints.md) gives commands and transitions. The [runtime notes](compatibility.md) explain how to work without delegation, Python, internet access or a renderer. The shared [contract dictionary](../../agent-plugins/shared/education/contracts.json), [evidence registry](../../agent-plugins/shared/education/evidence.json) and [subject adapters](../../agent-plugins/shared/education/adapters.json) each have one canonical file. The generator installs those files inside every education package at `references/education/`. In the canonical source checkout read them from `agent-plugins/shared/education/`.

## Worked projects

| Project | Reader material | Teacher or process record |
| --- | --- | --- |
| Ukrainian Grade 7 motion | [Three short chapters and exercises](examples/motion/learner.md) | [Teacher notes and key](examples/motion/teacher.md), [project](examples/motion/project.json) |
| Italian university entrance mathematics | [Quadratics and intercepts](examples/admission/learner.md) | [Key](examples/admission/teacher.md), [dated CISIA alignment and three-session plan](examples/admission/project.json) |
| Foundation Year | [Multi-week guide and cumulative practice](examples/foundation-year-study-guide.md) | [Teacher key](examples/foundation-year-teacher-key.md) |
| Secondary literature | [Original passage and close reading](examples/literature-close-reading.md) | [Rubric and readings](examples/literature-teacher-key.md) |
| Foreign language | [Italian practice with English instructions](examples/language-learning-session.md) | [Teacher prompts and key](examples/language-teacher-key.md), [synthetic diagnostic, event and analytics bundle](examples/language-learning-trace.json) |
| Research update | [Appraised source and rule export](../../agent-plugins/skills/education-learning-science/examples/project-export.json) | [Governed decision example](examples/governance-project.json) |

From the repository root, replay the real runner in separate processes. Supply an empty project directory or the journal for a previous run of that same example. The replay consumes existing teaching files and records stage acceptance. It does not author materials, simulate a student or invoke another model.

```sh
python docs/education/replay.py motion PATH_TO_PRIVATE_MOTION_JOURNAL
python docs/education/replay.py admission PATH_TO_PRIVATE_ADMISSION_JOURNAL --skill claude/skills/education-orchestrator
python codex/skills/education-orchestrator/scripts/workflow.py check docs/education/examples/language-learning-trace.json
python codex/skills/education-orchestrator/scripts/workflow.py inventory docs/education/examples/language-learning-trace.json
```

A private bundle is portable JSON. Export it only to an authorised recipient. The `inventory` command exports counts of four material types and no user-provided strings or learner counts. For public issues create a fresh synthetic reproducer. Omit responses, cohort identifiers, dates of birth, school names and free-text notes. Keep versioned observations and authorised decisions in the project folder, purge copies and journals under the agreed retention policy, and check any separate backup arrangements with their owner.

**Changing a shared rule.** Use the [research method](research-method.md) and [improvement governance](improvement-governance.md). A downstream user can send a portable proposal and synthetic patch after reviewing it for privacy. A maintainer can review, test and publish a new registry version. An individual learner's outcome stays with the project.

## Adapter and compatibility contract

Select records by subject and applicability, combine them for integrated teaching, and record chosen adapter IDs in the brief. Each adapter supplies a versioned ID, subject, notation, prerequisite patterns, misconception probes, explanation forms, assessment formats, access constraints, source list, status and applicability. A declared official edition controls assessed content, local conventions control presentation and the accessibility adjustment must preserve the target construct. Record conflicts explicitly before combining frameworks. No subject adapter establishes national alignment by itself.

Use current artefact revision references from the contract dictionary in each handoff. A producer owns its output fields. Reviewers add findings and analytics proposes updates. The orchestrator owns workflow state. The module can run with synthetic data and does not require a database, service account or learner identifier. See [evaluation and limits](evaluation.md) for the exercised scope.
