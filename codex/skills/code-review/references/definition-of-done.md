# Definition of Done

> Vendored from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/blob/7676817c12a1317454ae3898a0c5c1eacf5dd3d5/references/definition-of-done.md) at commit `7676817c12a1317454ae3898a0c5c1eacf5dd3d5` under the bundled MIT license.
> Repository-specific rules override this snapshot. Treat tool commands and numeric targets as advisory; the main skill's cost and approval gate still applies.

A standing, project-wide bar that a change must clear before it counts as done. Unlike task-specific acceptance criteria, a Definition of Done is reusable. Apply this reference only when the repository or user establishes such a gate.

## Definition of Done vs. Acceptance Criteria

| | Acceptance Criteria | Definition of Done |
|---|---|---|
| Scope | Specific to one task or spec | Applies to every increment |
| Changes | Different for each item | Fixed and reused |
| Answers | "Did we build *this thing*?" | "Is it *ready*?" |
| Owner | Defined when planning the task | Defined once for the project |
| Example | "User can reset password via email link" | "Tests pass, no regressions, docs updated" |

The two are complementary. A task is done only when **its** acceptance criteria are met **and** the standing Definition of Done is satisfied. Skipping either leaves work that looks finished but is not.

## The Standing Checklist

Apply this to every change before declaring it done.

### Correctness
- [ ] All acceptance criteria for the task are met
- [ ] Code runs and behaves as intended, verified at runtime, not just compiled or typechecked
- [ ] New behavior is covered by tests that fail without the change and pass with it
- [ ] Existing tests still pass; no regressions introduced
- [ ] Edge cases and error paths are handled, not just the happy path

### Quality
- [ ] Code reveals intent through naming and structure; no comments needed to explain *what* it does
- [ ] No duplicated business logic
- [ ] No dead code, debug output, or commented-out blocks left behind
- [ ] Changes are scoped to the task; no unrelated refactors snuck in
- [ ] Linting and formatting pass

Use the main code-review dimensions and repository conventions to interpret these items.

### Integration
- [ ] Change works with the rest of the system, not just in isolation
- [ ] Database migrations, config changes, and feature flags are accounted for
- [ ] Backward compatibility considered for any public interface or API change

### Documentation
- [ ] Public interfaces, APIs, and user-facing behavior are documented
- [ ] Architectural decisions worth preserving are recorded in the repository's normal decision log
- [ ] Documentation describes the current state in timeless language, not the change history

### Ship-readiness
- [ ] Security implications reviewed for any untrusted input, authentication, authorization, or sensitive-data handling
- [ ] Observability is appropriate for new critical paths (logs, metrics, traces)
- [ ] Rollback or recovery is defined for risky changes
- [ ] The human has reviewed and approved before merge or deploy

## How to Apply

- **Per task**: confirm the Correctness and Quality sections before checking the task off.
- **Per feature**: confirm Integration and Documentation before considering the feature complete.
- **Per release**: the full checklist is the floor; add the repository's deploy-specific gates.

Tailor the list to the project once, then reuse it unchanged. A Definition of Done that is renegotiated every sprint is not a Definition of Done.

## Red Flags

- "It's done, I just haven't run it yet": unverified work is not done.
- "Tests pass" used as a synonym for done while docs, regressions, or runtime verification are skipped.
- A different bar applied depending on deadline pressure.
- Acceptance criteria treated as the whole bar, with no standing quality floor.
- "Done" declared before human review on changes that need it.
