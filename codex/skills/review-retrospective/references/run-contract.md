# Run records and bounded preparation

Keep a compact capsule in an already-authorized report or handoff. Without an
artifact path, return it inline or reuse facts already present in the report.
Do not silently create a project journal, edit memory, or export private chats.

Capture start/end timestamps from the host clock and actual model/mode when
available. Obtain usage snapshots through an available, cheap, authorized host
status capability. If unavailable, leave them unknown without repeatedly asking
the user or inspecting credentials. Capture optional per-stage timing as stages
run; never reconstruct active compute time from wall time alone.

The helper accepts this versioned JSON shape. `null` means unknown. Artifact
references may be paths or stable conversation/source links. Keep secrets and
private source code out of public examples.

```json
{
  "schema_version": 1,
  "runs": [{
    "run_id": "review-2",
    "task_id": "import-retry",
    "skill": "code-review",
    "skill_revision": "release-or-commit",
    "input_revision": "base..head",
    "input_artifact": "review-input.md",
    "report_artifact": "review-2.md",
    "model": "exact-host-model-or-unknown",
    "mode": "standard",
    "stage": "whole-review",
    "scope": ["worker.py"],
    "outcome": "COMMENT",
    "coverage_limits": ["remote flags unavailable"],
    "captured_at": "2026-11-08T12:00:00+01:00",
    "timing": {"elapsed_seconds": 90, "waiting_seconds": null},
    "usage": {"input_tokens": 8000, "output_tokens": 1000,
              "cached_input_tokens": 2000, "reasoning_tokens": 200,
              "model_calls": 2},
    "limit_usage": [{
      "kind": "subscription", "window": "weekly", "source": "host status",
      "before_window_id": "week-A", "after_window_id": "week-A",
      "before_percent": 30, "after_percent": 32,
      "exclusive": false
    }],
    "upstream": [{"skill": "review-arch", "invoked": false}],
    "feedback": [{
      "event_id": "callback-retry", "kind": "missed-defect", "priority": "P1",
      "status": "verified", "evidence": "reproducer.md#result",
      "evidence_revision": "result-v2", "assessed_revision": "result-v1"
    }]
  }]
}
```

For each run retain the input/report identity, reviewed scope and revisions,
skill version, model/mode, outcome, coverage limits, and source capture times.
The prepared `runs` records preserve `stage`, `scope`, `outcome`,
`coverage_limits`, and `captured_at`; absent context stays `null`, not an empty
claim of coverage. Original inputs and sources must still be inspected.
Use stable run/event IDs. Change `evidence_revision` when the underlying evidence
changes, not merely when the case is reread. Update `assessed_revision` only after
assessment. Do not treat a previous proposed change as an applied improvement.

For an invoked upstream stage record `skill`, `invoked: true`, its `run_id`, and
`invocation_evidence`. Include that run's original input/report references in the
index. No entry means invocation is unknown and the check is skipped. An explicit
false entry is skipped. An unavailable report or different task is a limit, not
permission to reconstruct an imaginary review or start a new architecture pass.

Feedback kinds are `missed-defect`, `false-positive`, `severity`, `verdict`,
`cost`, and `clean-control`. Status is `verified`, `unverified`, or `disputed`.
The helper validates declared status, not truth. Inspect the actual evidence.
It sorts new cases by P0-P3, preserves their status, and reports deferred counts.

Token counts are actual host measurements or unknown. Cached input is a subset
of input and reasoning is a subset of output under this schema; never add them
again. If a provider uses another accounting convention, normalize only from
documented host data and retain the raw source. Do not sum overlapping parent
and child records. The helper emits per-run costs, not an account-wide total.

Elapsed time includes waiting. Record active/waiting or parallel agent durations
separately only when measured. Sums of concurrent stage durations are not wall
time. A slow run alone does not establish that its model caused the delay.

Limit percentages must identify kind, window, source, capture times, and reset
identity in the underlying artifact. Supported kinds are `subscription`,
`context`, and `stage-budget`; compare like with like. The helper emits a delta
in percentage points only for complete snapshots of the same window with no
decrease. Shared/unknown attribution keeps per-review consumption unknown.
`exclusive: true` requires evidence that the snapshots isolate this review.
Window resets, concurrent sessions, and missing snapshots limit comparisons.
Do not label an estimate as an observed percentage or compare different windows.

The default worklist cap is five new events. It bounds retrospective work, not
the original review findings or merge verdict. Use a project-authorized budget,
name deferred work, and stop after one assessment/validation cycle. Full model
comparisons and broad historical mining are separate bounded work, justified by
the signal and existing authorization.
