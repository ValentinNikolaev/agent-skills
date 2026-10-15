# uv Commands and Effects

Adapted from wshobson's uv-package-manager at commit `044b4b21f083948e69ec878a7b07c8d0951a6ffa`, with corrected command roles and explicit mutation/verification boundaries. See `LICENSE.wshobson-agents`. Verify flags against the installed uv before execution.

## Choose the interface

| Workflow | Source of truth |
| --- | --- |
| Project/workspace | Project metadata, workspace/source policy and `uv.lock` |
| `uv pip` | Explicit requirements/constraints and the selected environment; does not itself maintain the project's manifest and lock |
| `uv tool` / `uvx` | Isolated tool requirements; separate from application dependency selection |
| Standalone script | Script metadata and its chosen environment; do not silently turn it into a project |

## Inspection, consistency and mutation

These are command forms, not permission to execute them in every task. Resolve the owning project first. Network/cache access and project code execution are separate effects from tracked-file writes.

| Form | Purpose and effects |
| --- | --- |
| `uv --version`, `uv help lock` | Inspect tool version and supported command flags |
| `uv lock --check` | Check that a lock exists and remains consistent; fail for a missing/stale lock. Resolution may consult metadata/network/cache; not an environment install |
| `uv lock` | Create/update `uv.lock`; resolution may use network/cache. Does not install the application environment |
| `uv add <requirement>`, `uv remove <name>` | Intentionally change direct requirements and lock/environment according to options; placeholders must be replaced with authorized packages |
| `uv lock --upgrade-package <name>` | Targeted re-resolution; inspect transitive changes and constraints |
| `uv sync --locked` | Require a fresh lock, then synchronize the environment; installs/builds/removals can occur |
| `uv sync --frozen` | Synchronize from an existing lock without checking freshness; environment mutation still occurs |
| `uv run <configured command>` | May lock/sync, then executes project code and its effects |
| `uv run --locked <configured command>` | Require lock consistency before executing; environment synchronization/code effects remain |
| `uv export --locked --format requirements.txt` | Export the lock under a consistency gate; choose supported output/hash options using installed help |

`--no-sync`, `--offline` and `--frozen` do not make arbitrary execution safe. Offline mode needs cached artifacts; it is not proof that the lock matches current requirements. An existing environment is not necessarily the one CI/deployment uses.

Do not use `uv lock --no-install`: locking already has a different role from installing. Do not request hashes from `uv pip freeze --require-hashes`; freeze lists the installed environment. For lock-based export and hash policy use supported `uv export` options, or `uv pip compile` when the requirements workflow is authoritative.

## CI and migration checks

- Pin or otherwise deliberately select uv/Python versions according to repository policy. Check their compatibility, groups, extras, workspace package selection and platform targets.
- Use a freshness gate such as `uv lock --check` or a supported `--locked` command when drift must fail. If a Docker layer uses `--frozen`, identify the independent gate that catches stale declarations.
- Keep application locks separate from library publication metadata. An exported requirements file and a development environment freeze answer different questions.
- Review indexes and source priority, editable/path/Git dependencies, build isolation and credentials without printing secrets. Moving credentials or changing the dependency-confusion boundary is not routine formatting.
- Run only the requested upgrade. Resolver success does not prove runtime behavior, artifact availability on another platform, or security of build hooks.
- Diagnose errors from recorded command/version/project evidence. Missing uv or an unavailable artifact is an unrun check, not a reason to silently rewrite the workflow.

Primary references: [locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/), [CLI reference](https://docs.astral.sh/uv/reference/cli/), and [uv pip interface](https://docs.astral.sh/uv/pip/).
