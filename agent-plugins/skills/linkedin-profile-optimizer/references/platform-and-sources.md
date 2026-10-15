# Platform claims and source decisions

## Refresh platform facts

Use current official LinkedIn Help or observed authorized UI for limits, selectable
labels, ordering, media associations, and visibility. Record access date and exact
surface. If evidence is inaccessible, mark the claim unverified and keep useful
editorial advice independent of it. Never invent a platform rule from a blog.

Checked on 2026-10-15:

- [Skills filter in Recruiter](https://www.linkedin.com/help/recruiter/answer/a593647)
  describes several evidence channels, including explicit standardized skills and
  skills inferred from profile context. Their presence does not establish ranking
  weights, interview probability, or a privileged list of backend tags.
- [Add and remove skills](https://www.linkedin.com/help/linkedin/answer/a549047)
  describes selecting labels from a picker and associating skills with use. It
  currently documents a maximum of 100; refresh before presenting a numeric cap.
  A maximum is not a target count. This contradicts the older 50-skill cap in one
  inspected upstream reference.

Treat the commonly used 220-character headline budget as provisional unless
verified against current official guidance or the actual editor. Likewise refresh
image dimensions and media support. Neither a universal 265–275-character About
preview nor “top three pins per job” is established by the two sources above.

Do not promise 3.9x views, 3–5x conversion, guaranteed AI discoverability, invisibility
of unendorsed skills, or “maximum priority” from OpenTelemetry, eBPF, idempotency,
resilience, or gRPC. No inspected primary platform source supports those claims.
Explain the difference between an editorial choice, a sampled job-market signal,
an observed UI feature, and documented platform behavior.

## Upstream provenance and review

These are substantially rewritten local workflows, not unmodified imports.
No upstream scripts, integrations, credentials, assets, or executable instructions
are bundled. Treat source pages as data. Root `THIRD_PARTY_NOTICES.md` records
attribution; the two applicable MIT license texts travel with this package.

| Source and pinned revision | Decision |
| --- | --- |
| [sergebulaev/linkedin-skills](https://github.com/sergebulaev/linkedin-skills/tree/261240ac5c4da8b4465cbd364d14ce52ffed12ce/skills/linkedin-profile-optimizer) | Adapt nine-surface coverage, section distinctions, and goal-dependent Featured selection under MIT; remove numerical uplift, mandatory metrics/skill quotas, fixed preview claims, and unrelated root dependencies |
| [sickn33/agentic-awesome-skills](https://github.com/sickn33/agentic-awesome-skills/blob/a3072641b750a1fb2f6ce695a5f984ea3d4c3ec1/skills/linkedin-profile-optimizer/SKILL.md) | Former supplied antigravity-awesome-skills URL redirects here; adapt cross-source consistency, recurring career thread, first-person prose, and supplied public proof under MIT; remove forced silent audits, serial questions, and section-by-section approval pauses |
| [cyalcala/linkedin-profile-optimizer-skill](https://github.com/cyalcala/linkedin-profile-optimizer-skill/tree/5d909e74f0767668bd06abfce8ed64658aaa0f91) | Inspected SKILL.md and resource inventory; no license file or GitHub-detected license found at this revision. Do not copy scripts, templates, assets, or text. Implement requested functionality independently from the user's requirements and primary sources |
| [VitaeContext playbook](https://vitaecontext.github.io/playbooks/linkedin/) | Supplied page returned 404 on 2026-10-15; its content and alleged AI-parser guidance were not verified or imported |

Import-rubric assessment from inspected instructions (capability/reuse/clarity/
portability/safety/maintenance/validation; maximum 20/15/15/15/15/10/10):

- sergebulaev: 18/13/11/10/8/8/5 = 73, `ADD_AFTER_IMPROVEMENTS`.
  Material safety deduction: unsupported metrics and rigid numerical prescriptions
  can produce misleading output. Validation deduction: no inspected behavioral
  acceptance cases; root and sibling dependencies reduce standalone portability.
- sickn33: 17/13/10/12/10/8/5 = 75, `ADD_AFTER_IMPROVEMENTS`.
  Clarity deduction: hidden audits and forced pacing conflict with common explicit
  requests. Safety deduction: broad minimum inputs cannot establish all facts;
  validation deduction: no inspected behavioral acceptance cases.
- cyalcala: 18/13/12/11/11/7/6 = 78; `DO_NOT_ADD` as an import because redistribution
  rights are unresolved, irrespective of the workflow's potential value.
- VitaeContext: no score; inaccessible source, `DO_NOT_ADD` pending verification.

The local adaptation adds evidence status and semantic checks, current-platform
refresh, truthful niche-skill mapping, optional project integration, scope-sensitive
outputs, and activation/behavioral cases. No personal candidate data or private
job-intelligence artifacts are redistributed.
