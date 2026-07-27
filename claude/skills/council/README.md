# LLM Council

A shared agent skill that turns one high-stakes question into five expert perspectives, peer review, and a final verdict.

This folder is the canonical source for the Council skill in `ValentinNikolaev/llm-skills`. Edit it here, then regenerate the Claude and Codex distribution wrappers from the repo root.

## When to use it

Use Council when a decision has real uncertainty, tradeoffs, or meaningful downside if you get it wrong.

Good council questions:

- "Should I launch a $97 workshop or a $497 course?"
- "Which of these 3 positioning angles is strongest?"
- "I'm thinking of pivoting from X to Y. Am I crazy?"
- "Here's my landing page copy. What's weak?"
- "Should I hire a VA or build an automation first?"

Bad council questions:

- "What's the capital of France?" (one right answer, no need for perspectives)
- "Write me a tweet" (creation task, not a decision)
- "Summarize this article" (processing task, not judgment)

The council is useful when you want pressure, not validation. It is meant to surface what you are missing, where advisors disagree, and what the next move should be.

## Repo layout

```text
agent-plugins/skills/council/
├── SKILL.md     # Canonical skill instructions
└── README.md    # This file
```

Generated copies live outside this folder:

```text
claude/skills/council/
codex/skills/council/
```

Do not edit the generated copies directly. Update `agent-plugins/skills/council/`, then regenerate.

## Install from this repo

### Codex

Install the plugin from the Codex plugin marketplace:

```bash
codex plugin marketplace add ValentinNikolaev/llm-skills --ref master
codex plugin add agent-plugins@valentin-agent-plugins
```

Codex reads `.codex-plugin/plugin.json` and loads generated skills from `codex/skills/`.

### Claude Code

Install the plugin from inside Claude Code:

```text
/plugin marketplace add ValentinNikolaev/llm-skills@master
/plugin install agent-plugins@valentin-agent-plugins
/reload-plugins
```

Or install from a shell:

```bash
claude plugin marketplace add ValentinNikolaev/llm-skills@master
claude plugin install agent-plugins@valentin-agent-plugins
```

Claude reads `.claude-plugin/plugin.json` and loads generated skills from `claude/skills/`.

## Development

After editing `SKILL.md` or this README, regenerate the wrappers from the repo root:

```bash
python scripts/generate_skill_wrappers.py --clean
```

Then review the generated files before committing:

```bash
git diff -- agent-plugins/skills/council claude/skills/council codex/skills/council
```

## How to trigger it

Once installed, ask the agent to run Council with phrases like:

- "council this"
- "run the council on [your question]"
- "pressure-test this"
- "stress-test this"
- "war room this"

The agent should frame the question, gather relevant context, run the five advisors in parallel, anonymize their peer review, and return a single Council Verdict in chat.

## Credits

Original skill source: https://github.com/aiwithremy/claude-skills-llm-council/

Built by [Ole Lehmann](https://x.com/itsolelehmann).

The methodology is adapted from Andrej Karpathy's [LLM Council](https://github.com/karpathy/llm-council).
