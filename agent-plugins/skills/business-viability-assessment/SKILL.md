---
name: business-viability-assessment
description: Create an evidence-based project viability and financial assessment for a software product, startup idea, MVP, repository, PRD, requirements folder, or concept document. Use when the user asks whether a project is worth building, wants market demand research, competitor analysis, MVP scope reduction, development estimates, infrastructure and marketing costs, unit economics, financial scenarios, risks, validation experiments, or a GO / VALIDATE_FIRST / PIVOT / NO_GO recommendation. Work through CLI/project files, write only analysis artifacts, and do not modify product source code.
metadata:
  trigger: Assess software project viability, financial potential, MVP effort, costs, risks, and go/no-go recommendation
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(find:*), Bash(rg:*), Bash(python:*), WebSearch, WebFetch
argument-hint: "[project path, idea, PRD, or requirements folder] [quick|standard|deep]"
effort: thorough
---

# Business Viability Assessment

Assess a project like a product analyst, startup financial modeller, technical architect, and go-to-market analyst. Produce a grounded recommendation, not a pitch deck.

## Operating rules

- Work primarily through the console and available CLI tools.
- Treat repository files as project context and external research as evidence.
- Do not modify product source code.
- Create or update files only inside `analysis/business-viability/`.
- If the user provides optional parameters, use them. If parameters are missing, infer reasonable assumptions, label them with confidence, and continue.
- Use current public sources for market data, competitor pricing, infrastructure pricing, and relevant regulations. Cite sources with access dates.
- If web research tools are unavailable, produce a local-only draft, mark all market and pricing claims as unverified, and list the exact research gaps instead of inventing sources.
- Never invent statistics, competitors, prices, customer behavior, or sources.
- Do not let technical feasibility inflate the commercial recommendation.

## Depth Modes

Choose the smallest mode that satisfies the request:

- `quick`: inspect supplied context, identify the core hypothesis, competitor categories, top risks, rough MVP effort, and next validation step. Write only `executive-summary.md`, `assumptions.md`, and `sources.md`.
- `standard`: complete the required workflow and core artifacts from the assessment contract.
- `deep`: use the standard workflow plus deeper competitor/source research, sensitivity analysis, and a reproducible model script when calculations are non-trivial.

Default to `standard` unless the user asks for a fast pass, a lightweight opinion, or a full investor-grade assessment.

## Required reference

Read `references/assessment-contract.md` before starting the assessment. It defines the phase checklist, required output files, financial model schema, JSON schema, evidence rules, and final verdict rules.

## Workflow

1. Parse the user request for input paths and project parameters.
2. Inspect supplied files recursively, ignoring generated dependencies, vendor folders, build artifacts, caches, binary files, `.git`, and `node_modules`.
3. Summarize the project understanding before judging viability:
   - problem;
   - product;
   - target users and buyers;
   - value proposition;
   - MVP scope;
   - revenue model;
   - architecture;
   - unresolved assumptions;
   - contradictions;
   - likely validation-scope cuts.
4. Define the core business hypothesis and separate user, buyer, beneficiary, economic decision-maker, acquisition channel, trigger, workaround, switching cost, and refusal-to-pay reasons.
5. Research market demand and competitors with recent credible sources.
6. Build market sizing, pricing, development effort, infrastructure, marketing, unit economics, financial scenarios, risk analysis, and validation plan.
7. Write all required artifacts under `analysis/business-viability/`.
8. Verify the final quality checklist from the reference before finishing.

## Console progress

Print concise progress messages while working:

```text
[1/10] Inspecting project files
[2/10] Extracting product and MVP assumptions
[3/10] Researching demand and competitors
[4/10] Building market-size model
[5/10] Estimating development work
[6/10] Estimating infrastructure costs
[7/10] Estimating marketing and sales costs
[8/10] Building financial scenarios
[9/10] Defining validation experiments and kill criteria
[10/10] Writing final assessment
```

At completion, print the decision, confidence, MVP effort, MVP cash cost, break-even result, and `analysis/business-viability/` report path.
