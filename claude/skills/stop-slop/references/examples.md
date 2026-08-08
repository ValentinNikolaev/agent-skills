# Before-and-after examples

These examples preserve the facts available in each source. Bracketed text marks information the author must supply; it is not a claim.

## 1. Throat-clearing

**Before:**

> Here's the thing: building products is hard because customer needs change during development.

**After:**

> Building products is hard because customer needs change during development.

**Why:** Remove the opener without changing the causal claim.

## 2. Preserve qualification

**Before:**

> It turns out that most teams in our survey struggled with alignment because some participants would not admit they were confused.

**After:**

> Most teams in our survey struggled with alignment because some participants would not admit confusion.

**Why:** Remove throat-clearing while preserving `most`, `our survey`, and `some`.

## 3. Reduce jargon without adding evidence

**Before:**

> In today's fast-paced market, we need to lean into uncertainty and navigate launch risk with clarity.

**After:**

> We need to address launch risk despite the uncertainty.

**Why:** Replace jargon with plain language. Do not add claims about competitors, timing, or outcomes.

## 4. Combine dramatic fragments

**Before:**

> Speed. Quality. Cost. The plan cannot maximize all three under the current budget.

**After:**

> The current budget cannot maximize speed, quality, and cost at the same time.

**Why:** Combine fragments while preserving all three constraints.

## 5. Keep a useful contrast

**Before:**

> The failure came from missing permissions, not from an expired token.

**After:**

> The failure came from missing permissions, not from an expired token.

**Why:** The contrast carries diagnostic meaning, so the binary structure is useful.

## 6. Application opener without fabricated achievements

**Before:**

> I would like to apply for the Senior PHP/Laravel Developer role. I believe my background in Laravel, APIs, and backend development makes me a strong fit.

**After when no evidence is supplied:**

> I build Laravel APIs and backend systems. [Add one verified project result that demonstrates fit for this role.]

**After when the source supplies a verified result:**

> I build Laravel APIs and backend systems. On [verified project], I [verified result].

**Why:** Avoid a form-letter opener without inventing metrics, employers, or accomplishments.

## 7. Preserve protected text

**Before:**

> The API returns `403 Forbidden` when the caller lacks `reports:write`. Here's why that matters: clients must request the scope before retrying.

**After:**

> The API returns `403 Forbidden` when the caller lacks `reports:write`. Clients must request the scope before retrying.

**Why:** Remove meta-commentary while preserving code spans, status, scope name, and required sequence.

## 8. Review mode

**Source:**

> What if I told you the migration is not about speed, but about trust?

**Finding:** The rhetorical setup and binary pivot may sound formulaic. `Trust` is also undefined. Ask the author for the specific trust failure before rewriting; do not invent one.
