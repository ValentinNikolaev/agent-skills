# Structured finding contract

The reviewer decides what the code means; the helper validates evidence fields, keeps plausible findings, applies deep disagreement retention, and caps the display without hiding blockers from the merge decision. It does not discover bugs, prove quotes true, or measure review recall. Verify every quote against the cited current file (or the named before-image when explaining removed behavior).

The accompanying report's scope line lists the paths of references actually read and the required/completed finder passes with their partitions (or a linked pass ledger). For standard/deep, the coordinator must have read `references/finder-and-verifier.md` in full: a missing or truncated read fails the run as `INCOMPLETE` until completed, without a merge verdict or silent depth downgrade. Other unread applicable references or pass deficits remain named coverage limits. The helper enforces the mandatory path in the declared ledger, including when there are no candidates, but cannot observe file reads or executed passes; valid JSON alone cannot establish either. Selection, another reviewer's summary, and truncated output do not establish a full coordinator read.

Run `python scripts/prepare_review_report.py --input <json-file> --depth standard --max-findings 5`. Omit the cap for all findings. A JSON input path of `-` reads stdin. The helper is read-only and prints JSON; it does not contact the host or write a report. Keep temporary input outside the working checkout. When Python is unavailable, apply this contract inline and report the limit.

The input is an object with `verification_mode` (`independent` or `inline`), a `references_read` array of skill-relative paths actually read by the coordinator, and a `candidates` array. Standard/deep require the exact ledger entry `references/finder-and-verifier.md`; quick may omit the array and defaults to an empty ledger. A missing required entry or malformed ledger exits the CLI with status 2 and emits no report JSON. The output preserves the ledger. Inline mode must be disclosed in the review. Keep externally dependent Questions in the review record separately; do not invent an assessment when the mechanism cannot be established without outside evidence. Each assessed candidate has:

- `id`: stable `CR-<number>`;
- `finder`: identity used to enforce a different verifier in independent mode;
- `file`, `line`, `summary`, `failure_scenario`, `priority` (`P0`–`P3`), and `category` (`correctness`, `security`, `reliability`, `ui`, `ux`, `accessibility`, `performance`, `coverage`, `cleanup`, or `conventions`);
- `assessments`: one verifier assessment in quick/standard, or one or more in deep. Each has `reviewer`, `verdict`, and `evidence` containing `file`, positive `line`, and exact nonempty `quote`;
- each `PLAUSIBLE` assessment also has `confirmation`, the observation or check that would confirm it;
- each `REFUTED` assessment also has `refutation` (`contradicting-code`, `invariant-or-type`, `guard-in-diff`, or `no-observable-effect`) and `reason` explaining how that evidence rules out this scenario;
- a `conventions` candidate also has `rule` containing `file` and `quote`; its `file`/`line` identify the violation. A missing rule quote rejects this finding as unsupported policy, separately from code-proven refutation.

For example:

```json
{
  "verification_mode": "independent",
  "references_read": ["references/finder-and-verifier.md"],
  "candidates": [{
    "id": "CR-001",
    "finder": "finder-1",
    "file": "cache.py",
    "line": 9,
    "summary": "Cold-cache requests dereference a missing result",
    "failure_scenario": "cache miss -> None -> attribute access raises instead of returning a miss",
    "priority": "P1",
    "category": "correctness",
    "assessments": [{
      "reviewer": "verifier-1",
      "verdict": "PLAUSIBLE",
      "evidence": {"file": "cache.py", "line": 9, "quote": "return entry.value"},
      "confirmation": "Exercise the supported cold-cache configuration before any entry is populated."
    }]
  }]
}
```

Deduplicate mechanisms before using the helper; it rejects duplicate IDs rather than guessing equivalence. Standard/quick have one assessment per candidate. Deep retains any evidence-bearing non-refuted vote; disagreement with a refutation yields `PLAUSIBLE` with a check to resolve the conflicting evidence. All-refuted candidates remain in `refuted`, with their evidence, and do not consume the display cap. Unsupported convention candidates remain in `rejected` and do not consume it either. Do not describe these policy rejections as proof that a runtime defect is impossible.

Sort retained findings by priority first. Within the same priority, correctness/security/reliability/UI/UX/accessibility precede performance/coverage, then cleanup/conventions; ties use numeric CR-ID order. An optional nonnegative cap is applied only after sorting. Output includes displayed `findings`, `cut_count`, `omitted_ids`, total `retained_count`, and `has_blocker` computed from all retained P0/P1 findings before the cap. The merge verdict must also consider coverage gaps and material verification limits; the helper does not assign it.

For requested `ReportFindings` rendering, map each displayed finding's file, line, summary, failure_scenario, category and verdict to the exposed tool schema; the display cap applies to host rendering too. Compose `short_summary` in at most 60 characters and retain the CR ID through host-supported metadata or the summary. Host output does not replace coverage or the merge verdict. Re-report a verified fix with the same ID and the tool's supported outcome; do not invent fields the tool does not expose.

For `findings_file=PATH`, prepare the complete artifact without a display cap, then return a line for every retained finding, including P2/P3 UI/UX/accessibility findings. Use lowercase `ui`, `ux`, or `accessibility` as the structured category. `has_blocker=false` does not mean no findings. A source-grounded UI failure prescribed by the spec stays in Findings with its code location and `Origin: spec-driven defect` plus the spec section/excerpt.
