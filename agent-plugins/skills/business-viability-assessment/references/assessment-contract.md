# Assessment contract

Use this reference when running `$business-viability-assessment`.

## Inputs

Analyze the files and directories requested by the user. Optional parameters may include:

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

When a parameter is absent, infer a reasonable assumption, label it, explain confidence, and continue.

## Phase checklist

### 1. Project inspection

Prioritize files whose names include: `analysis`, `research`, `concept`, `mvp`, `requirements`, `spec`, `proposal`, `business`, `market`, `competitor`, `architecture`, `roadmap`, `pricing`, `customer`, `persona`, `problem`, `solution`, `README`.

Also inspect source code, configuration, deployment files, schemas, API specs, and infrastructure definitions when they help estimate implementation effort or costs.

Before judging the business, summarize:

1. problem being solved;
2. proposed product;
3. target users and buyers;
4. expected value proposition;
5. planned MVP scope;
6. revenue model, if present;
7. technical architecture;
8. important unresolved assumptions;
9. contradictions between files;
10. unnecessary features before core hypothesis validation.

Treat project-file claims as hypotheses unless supported by evidence.

### 2. Core business hypothesis

Express the project as:

```text
For [customer segment]
who experience [problem],
the product provides [solution],
which is better than [existing alternative]
because [differentiator].
Customers are expected to pay [pricing hypothesis]
through [revenue model].
```

Identify separately: user, buyer, economic decision-maker, beneficiary, acquisition channel, trigger that causes search, existing workaround, switching cost, and reason the customer may refuse to pay. If multiple unrelated segments exist, analyze each separately.

### 3. Market demand research

Use recent credible sources. Prefer official statistics, government or regulatory sources, public pricing pages, company reports, reputable research, marketplaces, app stores, search-demand indicators, customer reviews, relevant communities, job postings, competitor traffic, funding, customer counts, and revenue where credible.

For every important external claim record: source, publication or access date, geographic scope, what the source proves, and data limitations.

Separate:

- direct evidence: paying competitors, search demand, repeated review complaints, manual employment, growing software category, meaningful competitor adoption;
- indirect evidence: adjacent-industry growth, regulation, potential-user growth, enabling technical trends;
- weak or missing evidence: where demand remains speculative.

### 4. Competitive analysis

Identify direct competitors, indirect competitors, manual alternatives, open-source alternatives, internal company processes, and “do nothing.”

Create a comparison matrix covering target customer, core features, pricing, onboarding difficulty, integrations, strengths, weaknesses, positioning, switching barriers, adoption evidence, and differentiation.

Assess defensibility through proprietary data, workflow integration, distribution, brand/community, network effects, regulatory expertise, switching costs, operational efficiency, better economics, better UX, niche specialization, or speed. State when no durable advantage is visible.

### 5. Market sizing

Calculate approximate TAM, SAM, and realistic SOM for years 1, 2, and 3.

Use top-down and bottom-up approaches where possible. Bottom-up should weigh more heavily:

```text
reachable customers × realistic annual revenue per customer = obtainable annual revenue
```

Show formulas and assumptions. Do not present TAM as expected revenue.

### 6. Pricing and revenue model

Evaluate plausible models: one-time purchase, subscription, usage-based, freemium, transaction fee, marketplace commission, paid implementation, services, enterprise contract, advertising/sponsorship, or hybrid.

Recommend no more than three models. For each estimate entry price, average revenue per customer, gross margin, purchase frequency, churn/retention, sales complexity, payment-processing costs, support burden, pros, and cons.

Compare pricing against real alternatives and competitors. Distinguish price customers may accept, price required for viable economics, and price supported by evidence.

### 7. MVP scope review

Find the smallest product able to test:

1. problem importance;
2. willingness to try;
3. repeated use;
4. willingness to pay.

Classify major planned features as required for MVP, useful but deferrable, post-MVP, unnecessary before validation, or dangerous scope expansion.

Recommend manual or semi-manual operations when they validate demand more cheaply than automation. Describe primary user flow, admin/operational flow, payment flow, minimum analytics, minimum security, required integrations, and manualizable activities.

### 8. Development effort

Build a work breakdown structure with optimistic, realistic, and pessimistic person-hours, role, dependencies, uncertainty, and estimate explanation for: product clarification, UX/UI, backend, frontend, mobile if required, database, integrations, auth, payments, admin tools, analytics, infrastructure, CI/CD, observability, security, testing, docs, deployment, launch support, project management, and contingency.

Calculate:

- Scenario A: solo senior developer using AI tools, including founder time as economic cost;
- Scenario B: small product team;
- Scenario C: external agency or contractors, separating cash cost, economic cost, calendar duration, and person-hours.

Do not assume AI tools reduce all work equally. Use smaller productivity improvements for architecture, requirements, debugging, security, integrations, validation, and coordination. Add contingency of at least 15% for clear conventional MVPs, and 25–40% for unclear requirements, unusual integrations, AI features, regulatory complexity, or unfamiliar technology.

### 9. Infrastructure costs

Estimate monthly infrastructure for pilot, early, growth, and scale:

```yaml
pilot: 100 active users
early: 1_000 active users
growth: 10_000 active users
scale: 100_000 active users
```

Adjust tiers to better usage metrics when relevant: requests, uploaded files, generated tokens, transactions, tracked companies, monitored sources, processed jobs, storage volume.

Estimate application hosting, database, cache, object storage, backups, CDN, queues, email, SMS, payments, monitoring, logs, error tracking, domain/DNS, third-party APIs, AI models, search/vector DB, data collection, proxies/scraping infrastructure, security services, and support tools.

Compare at least two approaches such as low-cost VPS/PaaS, major cloud, serverless, or self-hosted open-source components. Include fixed monthly cost, variable cost per active user or transaction, scaling trigger, expected tier costs, and dominant cost component. Use current public prices where possible; otherwise provide formulas and ranges.

### 10. Marketing and sales costs

Design a go-to-market strategy suited to the segment. Analyze only relevant channels: SEO, content, communities, social, paid search/social, influencers, affiliates, marketplaces, app stores, direct outreach, LinkedIn, partnerships, events, cold email, PLG, free tools, referral, ABM.

For each relevant channel estimate setup effort, monthly cash budget, monthly labor hours, time to results, likely lead volume, conversion assumptions, CAC range, major risk, and cheap test.

Create launch-budget scenarios:

- Lean validation: smallest budget to test demand;
- Realistic launch: credible budget to reach initial paying customers;
- Accelerated launch: larger budget to acquire data/customers faster.

Do not recommend paid acquisition before checking LTV support. For B2B, distinguish self-service, founder-led sales, outbound sales, and enterprise sales. Include sales labor in CAC.

### 11. Unit economics

Calculate where applicable: ARPU, MRR, ARR, gross margin, contribution margin, CAC, LTV, LTV/CAC, CAC payback, monthly churn, annual retention, break-even customers, break-even revenue, burn, runway, payback period, and ROI.

Show formulas. Use ranges where evidence is weak. Do not use an LTV formula that assumes infinite lifetime.

Model pessimistic, base, and optimistic scenarios with customers acquired per month, conversion, price, churn, gross margin, marketing, infrastructure, labor, monthly revenue, monthly profit/loss, cumulative cash requirement, break-even month, and result after 12, 24, and 36 months.

Separate founder time, contractor salaries, infrastructure, marketing, software subscriptions, legal/accounting, taxes where known, and contingency. If tax jurisdiction is unknown, calculate pre-tax economics and say so.

### 12. Financial viability

Determine minimum cash required to launch, full economic MVP cost, monthly operating cost before meaningful revenue, required runway, break-even customer count, revenue required for one full-time developer, revenue required for a small team, likely investment recovery time, conditions that make the project attractive, and stop conditions.

Run sensitivity analysis on the highest-impact variables: price, conversion, retention, CAC, development cost, sales cycle, infrastructure cost, and frequency of use. Identify the two or three assumptions that dominate the result.

### 13. Risk analysis

Assess demand, willingness to pay, acquisition cost, sales cycle, competition, differentiation, technical complexity, third-party dependency, platform dependency, legal/regulatory constraints, privacy/security, data access, AI inference costs, model quality, scraping restrictions, operational workload, founder availability, support burden, and customer access.

For each material risk provide probability, impact, evidence, mitigation, cheap validation experiment, and decision threshold.

### 14. Validation plan

Minimize wasted development. Prefer this sequence:

1. problem interviews;
2. competitor and alternative analysis;
3. landing page or offer;
4. direct outreach;
5. pricing test;
6. concierge/manual prototype;
7. paid pilot or pre-order;
8. narrow technical prototype;
9. MVP;
10. expanded product.

For each experiment specify hypothesis, audience, execution method, cost, time required, success metric, minimum sample, pass threshold, fail threshold, and next decision.

Include explicit kill criteria, such as low qualified problem confirmation, no pilot commitment, impossible CAC, required price above willingness to pay, impractical technical/regulatory dependency, or insufficient retention.

## Evidence and uncertainty rules

Follow these strictly:

1. Do not fabricate statistics, competitors, prices, behavior, or sources.
2. Distinguish facts, calculations, assumptions, and opinions.
3. Label every important assumption high, medium, or low confidence.
4. Explain why each major assumption has that confidence.
5. Prefer ranges over false precision.
6. Use current prices and recent market information.
7. Include dates for prices and market data.
8. Cite external sources close to the relevant claim.
9. Explain when sources refer to adjacent rather than identical markets.
10. Do not treat competitor funding as proof of customer demand.
11. Do not treat market size as proof that this product can acquire customers.
12. Do not hide negative evidence.
13. Do not make the final score more positive because the project is technically feasible.
14. A technically interesting project may still be commercially weak.
15. Missing evidence must reduce confidence.

## Required output files

Create exactly these core artifacts under `analysis/business-viability/`:

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
financial-model.csv
assessment.json
```

When useful, create `analysis/business-viability/scripts/` with a small runnable script that regenerates the financial model. Prefer reproducible calculations over manually invented totals.

## Financial model CSV

Create 36 monthly projections. Recommended columns:

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

## Assessment JSON

Use this approximate structure:

```json
{
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
    "mvp_hours": {
      "optimistic": 0,
      "realistic": 0,
      "pessimistic": 0
    },
    "mvp_cash_cost": {
      "minimum": 0,
      "realistic": 0,
      "maximum": 0,
      "currency": "EUR"
    },
    "monthly_infrastructure": {
      "pilot": 0,
      "early": 0,
      "growth": 0,
      "scale": 0
    },
    "marketing_budget": {
      "lean_validation": 0,
      "realistic_launch": 0,
      "accelerated_launch": 0
    },
    "break_even": {
      "customers": 0,
      "monthly_revenue": 0,
      "estimated_month": null
    }
  },
  "recommendation": {
    "decision": "GO | VALIDATE_FIRST | PIVOT | NO_GO",
    "confidence": "HIGH | MEDIUM | LOW",
    "main_reasons": [],
    "critical_assumptions": [],
    "next_actions": [],
    "kill_criteria": []
  }
}
```

Scores must be 0–10 and supported by written evidence. Do not calculate the overall score as a naive average; commercial demand and willingness to pay must weigh more than technical feasibility.

## Executive summary opening

Begin `executive-summary.md` with:

```markdown
# Project viability assessment

## Verdict

**Decision:** GO / VALIDATE FIRST / PIVOT / NO-GO  
**Confidence:** High / Medium / Low  
**Commercial potential:** Low / Moderate / High / Very high  
**MVP effort:** X–Y person-hours  
**Estimated MVP cash cost:** €X–€Y  
**Estimated full economic cost:** €X–€Y  
**Pilot infrastructure:** approximately €X–€Y/month  
**Initial marketing validation:** approximately €X–€Y  
**Expected break-even:** month X, or not demonstrated  
**Maximum cumulative cash requirement:** approximately €X
```

Then include a concise explanation, strongest evidence in favor, strongest evidence against, main financial conclusion, most dangerous unsupported assumption, cheapest next validation step, what must be true for success, and clear recommendation.

## Verdict rules

- `GO`: use only when there is meaningful evidence of demand, plausible acquisition, acceptable economics, and manageable implementation risk.
- `VALIDATE_FIRST`: use when the project may be viable but willingness to pay, acquisition, retention, or market access remains insufficiently proven.
- `PIVOT`: use when the underlying problem appears real but the proposed customer, scope, pricing, channel, or solution is unlikely to work.
- `NO_GO`: use when realistic scenarios show weak demand, structurally poor economics, inaccessible customers, excessive risk, or a much better existing alternative.

Do not use `GO` merely because an MVP can be built.

## Final quality check

Before completion, verify:

- all supplied project files were considered;
- contradictions are documented;
- important numbers have formulas;
- current external prices have dates and sources;
- assumptions are separated from evidence;
- development effort includes testing and deployment;
- founder time is not treated as free;
- marketing labor is included;
- pessimistic, base, and optimistic scenarios exist;
- break-even is calculated;
- cash cost and economic cost are separated;
- conclusion contains explicit kill criteria;
- recommendation follows from evidence rather than enthusiasm.
