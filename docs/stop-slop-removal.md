# Stop Slop removal

The `stop-slop` skill was a deprecated compatibility entry through v29. It is
removed in v30. Its generated Claude and Codex copies are removed with it. The
removal is available to installed users only after a release that contains it is
published and their installation is updated.

| Former use | Replacement |
| --- | --- |
| Audit prose for AI-like phrases and structures | `ai-detector`, which analyzes locally unless the human also asks for the ChatGPT detector or another external check |
| Rewrite prose to remove those patterns | `humanizer`, which edits while preserving meaning and voice |
| Audit, then apply accepted findings | `ai-detector` first, then `humanizer` with the accepted findings |

No alias or compatibility copy is provided. An old `stop-slop` invocation does
not resolve to a new name on its own, so update saved prompts, workflows, and
instructions that name it.

A request that still names the removed skill describes a local analysis or an
edit. The old name never authorizes sending text to an external detector. Only the
human's own request for a detector or external check does.

## Update safely

1. Search saved prompts, workflows, and project instructions for `stop-slop` and
   replace each use with the skill in the table above.
2. For a managed plugin, use its normal update route after publication.
3. For a manual copy, delete the old `stop-slop` folder from the installation
   when you copy the updated `codex/skills/` or `claude/skills/` tree. A copy
   from an earlier version keeps working only as the unmaintained legacy entry.

## Provenance

The removed skill adapted [`hardikpandya/stop-slop`](https://github.com/hardikpandya/stop-slop)
under the MIT License. A comparison of its references with `ai-detector` and
`humanizer` found no surviving adapted passages, so its license file was removed
with it. [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) records the former
source. Earlier releases and the repository history retain the license text.
