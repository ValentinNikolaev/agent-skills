# Evidence and project integration

## Source hierarchy

Treat current user-confirmed source facts and designated candidate records as
evidence. Derived evidence banks are indexes to inspect, not independent truth.
Memory, old drafts, previous matches, search snippets, and profile slogans are
discovery aids. Reopen their underlying sources before making a factual claim.
An existing LinkedIn profile can establish current wording but cannot independently
resolve a contested metric. Record a source conflict and omit the disputed detail
until resolved; continue unaffected work.

For each published candidate assertion, retain an internal row:

| Field | Meaning |
| --- | --- |
| claim_id / section | Stable review identifier and destination |
| text | Exact final assertion, including any translated wording |
| source_id / locator | Supplied file and heading or public URL and revision/date |
| candidate_quote | Literal source substring, not a paraphrase |
| status | verified, unverified, cannot-confirm, or retracted |
| attribution | Employer/project, role, period, personal vs team scope |
| qualification | Units, baseline, time window, caveats, production vs prototype |
| public_use | public, anonymize, private, or unresolved |

Only verified facts with suitable public-use status support final public claims.
Verification requires checking the source's meaning and attribution, not merely
finding a number. Preserve “about,” team ownership, and measurement windows.
Never multiply a monthly estimate into an annual achievement or turn hours saved
into revenue without supporting evidence. Missing metrics can stay qualitative.

If hashing source snapshots, record the algorithm and normalization (for example,
UTF-8 text, BOM removed, CRLF normalized to LF, then SHA-256). A matching hash
proves snapshot identity, not truth. Changed sources invalidate prior verification.
Literal quotes establish traceability; semantic review establishes support.

Inspect public projects only within the supplied or authorized scope. Distinguish
repository ownership, code contribution, design authorship, and production use.
A demo's dependencies prove no employer deployment, performance result, or tenure.
Check README claims against relevant code, release, or author evidence when needed.

## Job-intelligence adapter

When the user names a job-intelligence project, resolve its root from the workspace
or supplied path. Do not hardcode a username, drive, database URI, or candidate.
Read its current `AGENTS.md`, workflow skill, candidate-source configuration,
quality contract, and relevant memory pointers before accessing project data.

For the inspected project's current structure, useful entry points are
`config/application-profile.yaml`, `registry/candidate/*.md`,
`registry/evidence/achievements.yaml`, `docs/application-quality.md`, and
`.agents/skills/job-intelligence-workflow/SKILL.md`. These are discovery hints;
confirm the live paths and configured sources instead of assuming their presence.

- Keep candidate source Markdown immutable. Check bank excerpts, hashes, status,
  employer/role/period, and corrections before reuse. Unverified, cannot-confirm,
  and retracted entries cannot support output. New candidate confirmation must
  follow the project's evidence workflow if persistence is explicitly requested.
- Candidate records and generated documents remain files. Live vacancy data is
  MongoDB-backed after cutover; frozen registry descriptions or metadata are not a
  fallback. Use the project's permitted read-only snapshot/export mechanism for
  explicitly selected postings. A read error is not permission to use stale data.
- Check same-project activity and access requirements before live storage access.
  Do not load credentials or query a database merely to draft a profile. Prefer
  supplied current exports when they suffice. Leave locks, cursors, statuses,
  registries, application packages, and notification queues untouched.
- Existing match scores and application prose may locate primary evidence; they
  cannot certify claims or become cross-vacancy keyword evidence. Preserve each
  posting's identity, direct text, and exact `jd_quote` separately. A multi-posting
  profile study is a separate task; do not feed its aggregate conclusions into an
  individual vacancy analysis or preparation package.
- Named-vacancy preparation gates, CV age/bullet quotas, application manifests,
  model profiles, and publication finalizers govern those workflows. Do not run
  them or impose CV layout rules merely because this task uses candidate sources.
  If the user requests an actual application, use that project's workflow instead.
- Reuse its evidence principles: exact candidate/JD quotes, explicit unknowns,
  source and version provenance, independent requirement assessment, and final
  semantic review. Do not relabel a historical judgment or approval as current.

Read the configured current personal voice before drafting profile prose or
recommendation requests. Keep local style extensions in their intended scope:
social comment review procedures and employer letter structures do not become
mandatory LinkedIn profile steps. Translate naturally while preserving facts and
the requested language level. Never persist new memory without explicit direction.
