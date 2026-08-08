# Quick assessment contract

Read this reference for advisory answers and quick artifacts. Do not load the full assessment contract unless the user requests standard or deep work.

## Inputs

Capture the available project or idea context, intended customer and buyer, geography, currency, forecast horizon, founder constraints, and evidence supplied by the user. Label inferred values.

## Minimum analysis

1. State the problem, product, buyer, user, and current alternative.
2. Identify the strongest direct demand evidence and the largest evidence gap.
3. Name direct, indirect, manual, open-source, and do-nothing alternatives when known.
4. Identify the smallest MVP or manual experiment that tests willingness to pay.
5. Give a rough optimistic, realistic, and pessimistic effort range.
6. Identify the dominant acquisition, pricing, retention, technical, and regulatory risks.
7. Recommend one cheapest next validation step with a pass threshold and fail threshold.
8. Return one verdict: `GO`, `VALIDATE_FIRST`, `PIVOT`, or `NO_GO`.

## Advisory output

Return in chat:

- verdict and calibrated confidence;
- concise project understanding;
- strongest evidence for and against;
- rough MVP effort and cost range in the requested currency;
- most dangerous unsupported assumption;
- cheapest validation step and kill criterion;
- inspected, sampled, and skipped scope;
- current-source gaps.

Do not write files.

## Quick artifact output

Only after explicit artifact authorization, create these files in the collision-safe report directory selected by the skill:

```text
executive-summary.md
assumptions.md
sources.md
coverage-manifest.md
```

Mark the report preliminary. State that market sizing, complete competitor research, a detailed work breakdown, infrastructure tiers, acquisition scenarios, unit economics, and a validated financial model were omitted.

Begin `executive-summary.md` with the canonical verdict enum, confidence, currency, forecast horizon, rough MVP effort and cost, and whether break-even was evaluated or remains undemonstrated.
