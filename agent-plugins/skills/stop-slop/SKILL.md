---
name: stop-slop
description: Deprecated compatibility entry for old stop-slop requests, planned for removal in v30. Use ai-detector for prose analysis and humanizer for authorized edits. Do not select for new writing tasks.
---

# Stop Slop (deprecated)

`stop-slop` is deprecated. Use `ai-detector` for AI-style analysis, including
targeted English phrase and structure audits. Use `humanizer` to apply authorized
edits while preserving meaning and voice. Do not run the former Stop Slop
workflow or add this name to new workflows.

## Handle an existing invocation

Briefly disclose the deprecation, then continue the requested work through the
replacement without asking the user to repeat the request.

- For analysis or findings, use `ai-detector` on the exact supplied passage.
- For a rewrite, use `humanizer`. Analysis alone does not authorize an edit.
- For analysis followed by an authorized rewrite, pass the accepted findings to
  `humanizer`. Preserve the user's facts, voice, scope and output constraints.
- An old `stop-slop` invocation alone does not request an external detector.
  Keep that handoff local. If the human also requests an AI detector or external
  check, follow `ai-detector`'s invocation rules and existing authorization.

## Removal in v30

Keep this compatibility entry through v29. Remove it in the v30 major release
along with its bundled legacy resources after checking maintained routing,
documentation and activation cases for old callers and documenting the
replacement in the release notes. External consumers are not fully observable,
so a clean repository search alone is insufficient. Until removal, restore a
missed caller by correcting this handoff rather than reintroducing the old
editing workflow.

The bundled references remain legacy material for provenance until removal.
They are not active editing instructions. Retain attribution and [LICENSE](LICENSE)
while those resources are distributed.
