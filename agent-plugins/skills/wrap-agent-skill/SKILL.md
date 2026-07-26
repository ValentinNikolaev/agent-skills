---
name: wrap-agent-skill
description: Create Claude and Codex wrapper skills from canonical agent-plugins-skills skills in this repository. Use when asked to add, update, sync, or adapt `agent-plugins-skills/skills/<name>` into `codex/skills/<name>` and `.codex/skills/<name>` wrappers without duplicating the canonical skill body.
metadata:
  trigger: Creating Claude/Codex wrappers for repository agent-plugins skills
user-invocable: true
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, MultiEdit
argument-hint: "<skill-name> [--claude] [--codex] [--sync]"
---

# Wrap Agent Skill

Create platform wrappers for an existing canonical skill under `agent-skills/skills/<skill-name>/`.

The canonical `agent-skills` skill owns the real instructions and bundled resources. The `codex` and `.codex` skills are thin wrappers that provide platform-specific frontmatter, then include the canonical body:

```md
@../../../agent-skills/skills/<skill-name>/SKILL.md
```

## Workflow

1. Confirm the source exists at `agent-skills/skills/<skill-name>/SKILL.md`.
2. Read the source `SKILL.md` frontmatter and body before writing wrappers.
3. Create or update `../../../codex/skills/<skill-name>/SKILL.md` for Claude/Cloud.
4. Create or update `.codex/skills/<skill-name>/SKILL.md` for Codex.
5. Re-read both wrappers and verify:
   - each wrapper name matches the source skill name
   - each wrapper points to `@../../../agent-skills/skills/<skill-name>/SKILL.md`
   - the Codex wrapper has at least `name` and `description` in YAML frontmatter
   - each wrapper keeps platform fields that are meaningful for that runtime

If a target path is blocked by permissions or ACLs, report the blocked file and provide the exact wrapper content that should be written.

## Codex Wrapper Rules

Codex routing depends on `name` and `description`, but repository wrappers may include extra frontmatter fields when the local Codex runtime, UI, or conventions use them. Do not strip existing useful fields just to make the wrapper minimal.

Minimal shape:

```md
---
name: <skill-name>
description: <Codex-specific trigger description>
---

@../../../agent-skills/skills/<skill-name>/SKILL.md
```

Extended shape, when useful:

```md
---
name: <skill-name>
description: <Codex-specific trigger description>
metadata:
  trigger: <short trigger summary>
user-invocable: true
allowed-tools: <minimal tool list if this repository uses tool allowlists>
argument-hint: "<expected user argument shape>"
---

@../../../agent-skills/skills/<skill-name>/SKILL.md
```

Write the Codex description for task routing. Include:

- what the skill does
- when Codex should use it
- common user phrasing that should trigger it
- important mode constraints, such as read-only behavior

For Codex, add extra fields only when they have a purpose in this repository. If an existing Codex wrapper uses `metadata`, `user-invocable`, `allowed-tools`, `argument-hint`, or `effort`, preserve and adapt those fields instead of deleting them. Avoid copied Cloud UI text that does not help Codex route or execute the skill.

## Claude Wrapper Rules

Claude/Cloud wrappers can use richer frontmatter. Preserve or adapt fields that help Cloud expose and run the skill.

Use this shape:

```md
---
name: <skill-name>
description: <Claude/Cloud trigger description>
metadata:
  trigger: <short human-facing trigger summary>
user-invocable: true
allowed-tools: <minimal tool list needed by the canonical skill>
argument-hint: "<expected user argument shape>"
---

@../../../agent-skills/skills/<skill-name>/SKILL.md
```

For Claude:

- Keep useful `metadata` from the source, such as `trigger`, `author`, or short UI-facing context.
- Keep `user-invocable: true` when the skill should be directly callable.
- Set `allowed-tools` to the smallest useful set for the canonical workflow.
- Add `argument-hint` when the skill accepts files, folders, PR numbers, text scopes, or mode flags.
- Keep source-specific fields such as `effort` only when they are meaningful for Claude/Cloud.
- Do not make the Claude description identical to the Codex description unless the platforms truly need the same routing text.

## Description Adaptation

Start from the source `agent-skills` description, then adapt per platform.

For Codex, prefer:

```yaml
description: <Action> in a Codex task. Use when the user asks to <specific triggers>. <Constraints or output expectations>.
```

For Claude, prefer:

```yaml
description: <Action>. Use when <Cloud/user-invocable triggers>. <Short constraint if important>.
```

Avoid vague descriptions like "helps with skills." The description is the routing surface.

## Tool Selection For Wrapper Allowlists

When a wrapper includes `allowed-tools`, choose them from the actual canonical workflow:

- Text-only editing or review: `Read, Grep, Glob`
- File creation or updates: `Read, Grep, Glob, Write, Edit, MultiEdit`
- Git diff or repository inspection: add `Bash(git diff:*), Bash(git status:*), Bash(git log:*), Bash(git show:*)`
- GitHub PR diff inspection: add `Bash(gh pr diff:*), Bash(gh pr view:*)`
- Avoid broad `Bash` unless the skill truly needs arbitrary shell commands.

When unsure, choose the narrowest set and mention the assumption in the final response.

## Do Not

- Do not copy the full `agent-skills` body into wrappers.
- Do not create extra README, changelog, or installation docs.
- Do not put meaningless Claude/Cloud fields into Codex wrappers.
- Do not overwrite a handcrafted wrapper without reading it first.
- Do not "normalize" the canonical `agent-skills` skill unless the user explicitly asks.

## Example

For `agent-skills/skills/stop-slop/SKILL.md`, create:

```md
claude-skills/skills/stop-slop/SKILL.md
.codex/skills/stop-slop/SKILL.md
```

Both wrappers should include the canonical body:

```md
@../../../agent-skills/skills/stop-slop/SKILL.md
```

The Codex wrapper may be minimal or extended depending on repository convention. The Claude wrapper should keep Cloud-specific metadata, invocation hints, and tool permissions.
