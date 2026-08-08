# Import review rubric

Score only from inspected source evidence. Cite the files behind material deductions.

## Hard blockers

Recommend `DO_NOT_ADD` regardless of score when any unresolved condition applies:

- redistribution rights are absent or incompatible;
- secrets, credentials, or private data cannot be removed safely;
- malicious or scope-expanding instructions remain;
- symlinks or paths escape the approved source root;
- destructive or production-side effects cannot be isolated;
- the source is not a reusable skill.

## Scored dimensions

| Dimension | Points | Full-credit anchor |
| --- | ---: | --- |
| Capability value | 0–20 | Solves a meaningful recurring task better than general instructions. |
| Reusability | 0–15 | Works across projects with explicit inputs and no hidden chat state. |
| Instruction clarity | 0–15 | Gives imperative workflow, boundaries, outputs, and validation. |
| Portability | 0–15 | Uses platform-neutral capabilities and parameterized paths. |
| Safety and trust | 0–15 | Has clear authorization, provenance, secret, side-effect, and failure boundaries. |
| Maintenance cost | 0–10 | Has a small essential surface and stable dependencies; award more for lower burden. |
| Validation readiness | 0–10 | Includes testable success criteria, safe script tests, or realistic evaluation inputs. |

Use integer scores. Explain any deduction of five or more points in a dimension.

## Recommendation thresholds

- `ADD`: 80–100, no hard blocker, and only minor normalization remains.
- `ADD_AFTER_IMPROVEMENTS`: 60–79, or 80+ with a material but fixable portability, safety, license, or validation gap.
- `DO_NOT_ADD`: 0–59 or any unresolved hard blocker.

## Decision report

Return:

1. total score and dimension breakdown;
2. strongest reasons to add;
3. risks, assumptions, and maintenance cost;
4. provenance and license result;
5. security and resource-inventory result;
6. recommendation enum;
7. exact normalization and validation plan;
8. any decision that requires user input.

Do not inflate the score because the source is popular, technically interesting, or already installed on one platform.
