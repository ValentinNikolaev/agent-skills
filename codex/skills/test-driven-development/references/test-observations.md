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
