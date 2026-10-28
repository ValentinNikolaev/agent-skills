# Test Observations

Choose an observation that distinguishes a plausible wrong implementation from the required behavior. These examples explain test design; use the repository's actual runner and language.

## Independent expected values

For a cart with prices 10 and 5, a worked example gives total 15. Assert that result. Recomputing the total with the same reduction and rounding algorithm as production can reproduce the same defect in the expected value.

For a rounding rule, choose an input where the plausible wrong rule differs, and derive the expected amount from the stated business rule. Do not invent a rounding policy to manufacture a failing test.

## Observable boundaries

If the requirement is that a created record can be retrieved, create it through the public interface, retrieve it, and assert the required fields. A test tied only to the name of an internal repository method can fail after a behavior-preserving refactor.

If the requirement is that a transaction commits atomically, an isolated database observation can be the correct boundary. If the requirement is one payment attempt per idempotency key, an observed external call count can be the contract. Choose based on the behavior, not a blanket ban on mocks or database assertions.

## Negative controls and vertical slices

For a parser fix, choose the smallest malformed input that the original parser mishandled. Observe the relevant assertion fail before the fix, then pass after it. A missing dependency or a filter selecting no tests does not establish this failure.

Add the next case after the first cycle teaches something about the implementation. Keep refactoring inside the red-green-refactor workflow and re-run the relevant cases afterward. Use `prove-checks` for a separate investigation of whether an existing green signal can detect its claimed defect.

## Scope and reuse

Before creating another test, identify the plausible wrong behavior it distinguishes and inspect nearby cases. Extend an existing case or parameterize equivalent inputs, such as supported locales, when that preserves a clear failure signal. Keep separate positive, negative, and security cases when they catch different regressions; fewer tests is not itself the goal.

Do not retest unrelated application defaults or established framework behavior merely because the feature uses them. Test the integration when the change can break it. A global locale change belongs to its own configuration contract rather than a feature-specific welcome-mail suite.

### Human-facing copy and contractual strings

Follow repository rules for messages and translations. Unless exact wording is an explicit requirement, a welcome-mail test should check substituted user data, required links, alias presence or absence, output formats, and escaping rather than hard-code its greeting, subject, footer, or surrounding translated prose. A benign example association name does not need repeated assertions; an adversarial value that exposes broken escaping can justify a focused case.

Preserve exact assertions when the bytes are the contract, such as a serialized protocol, stable error code, required legal wording, or security-sensitive escaping. An explicitly requested copy or localization regression can also need exact text checks where repository policy allows them. Distinguish those cases from incidental UX wording rather than banning all string assertions or testing every translation by default.
