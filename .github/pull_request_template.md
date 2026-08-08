## Summary

<!-- What problem does this change solve, and how? -->

## Related Issues

<!-- Use "Closes #123" when applicable. -->

## Change Type

- [ ] Canonical skill or shared resource
- [ ] New skill
- [ ] Generator, validator, or test
- [ ] Documentation or repository metadata
- [ ] Release or workflow change
- [ ] Breaking change

## Validation

<!-- List the commands you ran and their results. -->

```text
python scripts/validate_skills.py
python scripts/generate_skill_wrappers.py --clean --strict-links
python -m unittest discover -s tests -v
python scripts/generate_skill_wrappers.py --check --clean --strict-links
```

## Checklist

- [ ] I made changes in canonical sources rather than generated copies.
- [ ] I regenerated `claude/skills/`, `codex/skills/`, and `README.md` when required.
- [ ] I added or updated tests and activation cases when behavior changed.
- [ ] I checked local Markdown links and preserved required attribution.
- [ ] I removed secrets, credentials, and private data from the change.
- [ ] I documented breaking changes, migration steps, and security implications.
- [ ] I have read and followed `CONTRIBUTING.md` and the Code of Conduct.
