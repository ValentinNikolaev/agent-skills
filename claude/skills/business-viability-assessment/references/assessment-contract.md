# Standard and deep assessment contract

Read this reference only for explicitly requested standard or deep artifact assessments.

## Contents

- [Inputs and scope](#inputs-and-scope)
- [Project understanding](#project-understanding)
- [Demand and competition](#demand-and-competition)
- [Market size and pricing](#market-size-and-pricing)
- [MVP and development effort](#mvp-and-development-effort)
- [Infrastructure and go-to-market](#infrastructure-and-go-to-market)
- [Unit economics and financial viability](#unit-economics-and-financial-viability)
- [Risks and validation](#risks-and-validation)
- [Evidence rules](#evidence-rules)
- [Required artifacts](#required-artifacts)
- [Financial model CSV](#financial-model-csv)
- [Assessment JSON](#assessment-json)
- [Verdict rules](#verdict-rules)
- [Final quality check](#final-quality-check)

## Inputs and scope

Use user-supplied parameters. Otherwise label reasonable defaults and their confidence.

```yaml
target_markets: []
target_customers: []
currency: EUR
forecast_horizon_months: 36
founder_context:
  developers:
  weekly_hours_available:
  technical_level:
  use_of_ai_coding_tools: true
constraints:
  maximum_mvp_budget:
  desired_launch_date:
  preferred_cloud:
```

Accept any ISO 4217 currency code or a clearly identified user-defined unit. Use that currency consistently in prose, CSV values, and JSON. Do not substitute a currency symbol from the template.

Use the requested positive forecast horizon. Default to 36 months only when the user supplies no horizon.

Prioritize files named for analysis, research, concepts, requirements, specifications, proposals, business, markets, competitors, architecture, roadmaps, pricing, customers, personas, problems, solutions, and README content. Inspect source, configuration, schemas, API specifications, deployments, and infrastructure only as needed to understand scope and cost.

Create `coverage-manifest.md`; do not claim every supplied file was read. Record:

- supplied roots and repository state;
- selection and sampling rules;
- inspected files and why they mattered;
- ignored generated/vendor/cache/binary files;
- inaccessible and out-of-scope files;
- contradictions and unresolved gaps.

## Project understanding

Summarize before judging:

1. problem;
2. product;
3. users, buyers, decision-makers, and beneficiaries;
4. value proposition;
5. planned MVP;
6. revenue model;
7. architecture;
8. unresolved assumptions;
9. contradictions;
10. features that do not test the core hypothesis.

Express the hypothesis as:

```text
For [customer segment]
who experience [problem],
the product provides [solution],
which is better than [existing alternative]
because [differentiator].
Customers are expected to pay [pricing hypothesis]
through [revenue model].
```

Identify the acquisition trigger, current workaround, switching cost, and reason a buyer may refuse to pay. Analyze unrelated segments separately.

## Demand and competition

Use recent credible sources. Prefer official statistics, government or regulatory sources, public pricing pages, company reports, reputable research, marketplaces, app stores, customer reviews, relevant communities, job postings, and credible adoption or revenue evidence.

For each material external claim, record the source, publication or access date, geography, what it supports, and its limitations.

Separate:

- **Direct evidence**: paying alternatives, repeated buyer complaints, search or procurement behavior, manual labor, credible adoption, and retention.
- **Indirect evidence**: adjacent growth, regulation, enabling technology, or growth in potential users.
- **Missing evidence**: willingness to pay, channel access, retention, or behavior that remains speculative.

Compare direct competitors, indirect competitors, manual processes, open-source options, internal processes, and doing nothing. Cover customer, use case, pricing, onboarding, integrations, strengths, weaknesses, positioning, switching barriers, adoption evidence, and differentiation.

Assess defensibility through proprietary data, workflow integration, distribution, brand/community, network effects, regulatory expertise, switching costs, operational efficiency, economics, UX, specialization, or speed. State when no durable advantage is visible.

## Market size and pricing

Estimate TAM, SAM, and a realistic SOM for the modeled years. Use top-down and bottom-up evidence where possible, but weight bottom-up reachability more heavily:

```text
reachable customers × realistic annual revenue per customer = obtainable annual revenue
```

Show formulas and assumptions. Never present TAM as expected revenue.

Evaluate only plausible pricing models. Recommend at most three. For each, estimate entry price, average revenue per customer, gross margin, purchase frequency, retention/churn, sales complexity, payment cost, support burden, advantages, and drawbacks.

Distinguish:

- price customers may accept;
- price required for viable economics;
- price supported by evidence.

## MVP and development effort

Find the smallest product or manual service that tests:

1. problem importance;
2. willingness to try;
3. repeated use;
4. willingness to pay.

Classify planned features as required now, deferrable, post-MVP, unnecessary before validation, or dangerous scope expansion. Prefer concierge or semi-manual operations when they test demand more cheaply.

Describe the primary user flow, operational/admin flow, payment flow, minimum analytics, minimum security, required integrations, and manualizable work.

Build a work breakdown with optimistic, realistic, and pessimistic person-hours, roles, dependencies, uncertainty, and explanation for applicable work: clarification, UX, backend, frontend, mobile, data, integrations, authentication, payments, admin, analytics, infrastructure, CI/CD, observability, security, testing, documentation, deployment, launch support, management, and contingency.

Model:

- solo experienced developer using AI tools, with founder time valued;
- small product team;
- agency or contractors, separating cash, economic cost, duration, and person-hours.

Do not apply one AI-productivity multiplier to every task. Use smaller improvements for requirements, architecture, debugging, integrations, security, validation, and coordination. Add at least 15% contingency for a clear conventional MVP and 25–40% for unclear requirements, unusual integrations, AI features, regulation, or unfamiliar technology.

## Infrastructure and go-to-market

Choose usage tiers that match the product. The following are defaults, not requirements:

```yaml
pilot: 100 active users
early: 1_000 active users
growth: 10_000 active users
scale: 100_000 active users
```

Replace active users with requests, files, tokens, transactions, monitored entities, jobs, or storage when more meaningful.

Estimate applicable hosting, database, cache, object storage, backups, CDN, queues, email, SMS, payments, monitoring, logs, error tracking, domain/DNS, third-party APIs, AI models, search/vector storage, data collection, proxies, security, and support tools.

Compare at least two viable infrastructure approaches. Include fixed monthly cost, variable unit cost, scaling trigger, expected tier cost, and dominant cost. Use current public prices or show formulas and ranges.

Analyze only channels suited to the segment. For each, estimate setup effort, monthly cash, labor hours, time to results, lead volume, conversion assumptions, CAC range, risk, and a cheap test.

Create lean-validation, realistic-launch, and accelerated-launch scenarios. Do not recommend paid acquisition before checking LTV support. For B2B, distinguish self-service, founder-led, outbound, and enterprise sales; include sales labor in CAC.

## Unit economics and financial viability

Calculate applicable ARPU, MRR, ARR, gross margin, contribution margin, CAC, LTV, LTV/CAC, CAC payback, churn, retention, break-even customers and revenue, burn, runway, payback, and ROI.

Show formulas. Use finite-horizon or retention-curve LTV rather than an infinite-lifetime formula.

Model pessimistic, base, and optimistic scenarios for every month in `forecast_horizon_months`. Include customers, conversion, price, churn, gross margin, marketing, infrastructure, labor, revenue, profit/loss, cumulative cash requirement, break-even month, and outcomes at meaningful horizon checkpoints.

Separate founder time, contractors or salaries, infrastructure, marketing, software, legal/accounting, taxes when known, and contingency. If jurisdiction is unknown, report pre-tax economics.

Determine launch cash, full economic MVP cost, pre-revenue operating cost, runway, break-even count, revenue needed for one developer and a small team, recovery time, attractive conditions, and stop conditions.

Run sensitivity analysis on the highest-impact variables. Identify the two or three assumptions that dominate the result.

## Risks and validation

Assess demand, willingness to pay, acquisition, sales cycle, competition, differentiation, technical complexity, third-party and platform dependencies, law/regulation, privacy/security, data access, AI cost and quality, scraping limits, operations, founder availability, support, and customer access.

For each material risk, provide probability, impact, evidence, mitigation, cheap experiment, and decision threshold.

Prefer this validation sequence when applicable:

1. problem interviews;
2. alternatives research;
3. landing page or offer;
4. direct outreach;
5. pricing test;
6. concierge prototype;
7. paid pilot or preorder;
8. narrow technical prototype;
9. MVP;
10. expansion.

For each proposed experiment, specify hypothesis, audience, method, cost, duration, success metric, minimum sample, pass threshold, fail threshold, and next decision. Include explicit kill criteria.

## Evidence rules

1. Do not fabricate statistics, competitors, prices, behavior, or sources.
2. Distinguish evidence, calculation, assumption, and judgment.
3. Label material assumptions `HIGH`, `MEDIUM`, or `LOW` confidence and explain why.
4. Prefer ranges over false precision.
5. Date current prices and market data.
6. Cite sources near supported claims.
7. Explain adjacent-market evidence.
8. Do not treat funding, market size, or technical feasibility as demand proof.
9. Preserve negative evidence.
10. Reduce confidence when evidence is missing.

## Required artifacts

Create these files in the collision-safe report directory for standard and deep modes:

```text
executive-summary.md
project-understanding.md
market-demand.md
competitors.md
mvp-scope.md
development-estimate.md
infrastructure-costs.md
marketing-plan.md
unit-economics.md
risks-and-validation.md
assumptions.md
sources.md
coverage-manifest.md
financial-model.csv
assessment.json
```

For deep mode, also create a small runnable calculation script when the model contains derived totals or nontrivial scenario logic. Keep it inside the report directory and document its runtime and inputs.

Do not overwrite a pre-existing report directory. If the user explicitly requests an update, inspect the existing report and preserve a reviewable diff.

## Financial model CSV

Create one row for every scenario and month from 1 through `forecast_horizon_months`. Include at least `pessimistic`, `base`, and `optimistic` scenarios.

Use these columns:

```text
scenario
month
new_customers
active_customers
churned_customers
arpu
revenue
payment_fees
variable_infrastructure
fixed_infrastructure
marketing_cost
sales_cost
development_cost
support_cost
other_cost
total_cost
gross_profit
operating_profit
cumulative_cash_flow
```

Use plain numeric values in the configured currency; do not embed symbols or thousands separators. Document formulas and currency in `unit-economics.md` and `assessment.json`.

Use these formulas for every scenario and month. Set prior-month active customers and cumulative cash flow to zero for month 1:

```text
active_customers[m] = active_customers[m-1] + new_customers[m] - churned_customers[m]
revenue[m] = active_customers[m] × arpu[m]
total_cost[m] = payment_fees[m]
              + variable_infrastructure[m]
              + fixed_infrastructure[m]
              + marketing_cost[m]
              + sales_cost[m]
              + development_cost[m]
              + support_cost[m]
              + other_cost[m]
gross_profit[m] = revenue[m] - payment_fees[m] - variable_infrastructure[m]
operating_profit[m] = revenue[m] - total_cost[m]
cumulative_cash_flow[m] = cumulative_cash_flow[m-1] + operating_profit[m]
```

Put refunds, taxes, one-time launch charges, or other modeled cash costs that are not represented by a dedicated column in `other_cost` and explain them in `unit-economics.md`. Keep customer-count and currency units consistent within a scenario.

Calculate with full available precision before serialization. The validator accepts a derived value when it differs from the formula by at most an absolute `0.02` currency units or a relative `1e-9`, whichever tolerance is larger. Do not use the tolerance to conceal inconsistent rounding or formulas.

## Assessment JSON

Use this structure:

```json
{
  "meta": {
    "mode": "standard",
    "currency": "EUR",
    "forecast_horizon_months": 36,
    "generated_at_utc": ""
  },
  "project": {
    "name": "",
    "summary": "",
    "target_customer": "",
    "business_model": ""
  },
  "scores": {
    "problem_severity": 0,
    "evidence_of_demand": 0,
    "willingness_to_pay": 0,
    "market_accessibility": 0,
    "competitive_position": 0,
    "mvp_feasibility": 0,
    "unit_economics": 0,
    "scalability": 0,
    "overall_viability": 0
  },
  "estimates": {
    "mvp_hours": {"optimistic": 0, "realistic": 0, "pessimistic": 0},
    "mvp_cash_cost": {"minimum": 0, "realistic": 0, "maximum": 0, "currency": "EUR"},
    "break_even": {"customers": 0, "monthly_revenue": 0, "estimated_month": null}
  },
  "recommendation": {
    "decision": "VALIDATE_FIRST",
    "confidence": "LOW",
    "main_reasons": [],
    "critical_assumptions": [],
    "next_actions": [],
    "kill_criteria": []
  }
}
```

Replace example values with configured inputs. Keep scores from 0 to 10 and support each in prose. Use these anchors consistently:

- `0–2`: absent, contradicted, or structurally poor;
- `3–4`: weak and mostly assumed;
- `5–6`: plausible with material gaps;
- `7–8`: supported by multiple relevant signals;
- `9–10`: unusually strong direct evidence.

Do not compute overall viability as a naive average. Explain the weighting in `executive-summary.md` or `unit-economics.md`.

## Verdict rules

Use exactly one machine-stable enum in every artifact:

- `GO`: meaningful demand evidence, plausible acquisition, acceptable economics, and manageable implementation risk.
- `VALIDATE_FIRST`: possible viability, but willingness to pay, acquisition, retention, or access remains insufficiently proven.
- `PIVOT`: a real problem exists, but the proposed segment, scope, price, channel, or solution is unlikely to work.
- `NO_GO`: realistic scenarios show weak demand, structurally poor economics, inaccessible buyers, excessive risk, or a clearly superior alternative.

Do not use `GO` merely because an MVP is buildable.

Begin `executive-summary.md` with the verdict enum, confidence, currency, horizon, MVP effort, cash and economic cost, pilot infrastructure, initial validation budget, break-even result, and maximum cumulative cash requirement. Use the configured currency code or symbol consistently.

## Final quality check

Before handoff, verify:

- coverage is bounded and documented rather than called exhaustive;
- contradictions and negative evidence remain visible;
- formulas support important numbers;
- prices and market data have dates and sources;
- assumptions remain distinct from evidence;
- testing, deployment, founder time, and marketing labor are included;
- three financial scenarios span the configured horizon;
- cash and economic cost are separated;
- break-even and cumulative cash are calculated;
- kill criteria and the cheapest next experiment are explicit;
- currency and verdict enum are consistent across files;
- the bundled validator passes for the report directory.
