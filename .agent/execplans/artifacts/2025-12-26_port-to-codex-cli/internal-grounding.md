# Internal Grounding — Continuous-Codex Repo Scan

Timestamp: 2025-12-26

## What this repo is today

This repository is a **“Continuous Claude” kit**: a continuity + tooling layer designed around **Claude Code** concepts (hooks, agents, plugins, `.claude/` structure), plus an **agent-agnostic Python MCP runtime** and a **SQLite “artifact index”** used to recall prior handoffs/decisions.

It is *not yet* a Codex CLI-native kit: there is currently **no `.codex/` directory** in the repo, and most docs/scripts default to `.claude/*` paths.

## Core components (ground truth)

### Claude Code integration (currently primary)

- `.claude/settings.json`: registers Claude Code hook events (SessionStart, PreCompact, PostToolUse, etc.) and a `statusLine` command.
- `.claude/hooks/`: TypeScript + bundled JS used by hooks. Notable continuity hooks:
  - `.claude/hooks/src/session-start-continuity.ts`: loads the most recent `thoughts/ledgers/CONTINUITY_CLAUDE-*.md` into context on `resume|clear|compact`, and optionally includes the latest handoff and “unmarked outcomes” hints from the artifact DB.
  - `.claude/hooks/src/pre-compact-continuity.ts`: auto-handoff before compaction (Claude-only).
  - `.claude/hooks/src/handoff-index.ts`: indexes a newly written handoff into SQLite (Claude-only, because it depends on a Write hook).
  - `.claude/hooks/src/post-tool-use-tracker.*`: tracks edits/builds (Claude-only).
- `.claude/skills/`: Claude Code skills (SKILL.md directories) for ledger/handoff workflows, TDD guidance, hooks debugging, research, etc. These are **Claude Code format** (often missing `name:` frontmatter expected by Codex skills).
- `.claude/agents/`: Claude Code “agents” configs (plan-agent / validate-agent / debug-agent / etc).
- `.claude/plugins/braintrust-tracing/`: Claude-only plugin integration.
- `.claude/rules/`: Claude-only behavioral rules (not Codex execpolicy rules).

### Continuity data model (shared across agents, but paths are Claude-biased)

- **Ledger** (session state): `thoughts/ledgers/CONTINUITY_CLAUDE-<stream>.md`
  - Intended to be updated before `/clear`/context resets.
  - Currently **gitignored** by `CONTINUITY_CLAUDE-*` and by the top-level `thoughts/` ignore.
- **Handoffs** (cross-session transfer): `thoughts/shared/handoffs/<stream>/YYYY-MM-DD_HH-MM-SS_description.md`
  - These live under `thoughts/shared/…` which is explicitly *unignored* in `.gitignore`, so handoffs are intended to be shareable/trackable.
- **Artifact index** (SQLite + FTS): default DB path is **project-local** `.claude/cache/artifact-index/context.db`
  - Schema: `scripts/artifact_schema.sql`
  - Indexer: `scripts/artifact_index.py` (`--handoffs`, `--plans`, `--continuity`, `--all`, `--file`)
  - Query: `scripts/artifact_query.py`
  - Outcome marker: `scripts/artifact_mark.py`

### Agent-agnostic “MCP code execution” runtime (reusable with Codex CLI)

- Python package (pyproject name: `mcp-execution`) under `src/runtime/*`:
  - `src/runtime/harness.py`: runs Python scripts with MCP client initialization + cleanup.
  - `src/runtime/mcp_client.py`: lazy MCP client manager; **merges** project config (`.mcp.json` or `mcp_config.json`) with a **global config at `~/.claude/mcp_config.json`**.
  - `src/runtime/generate_wrappers.py`, `src/runtime/discover_schemas.py`: codegen tooling for MCP wrappers / inferred types.
- `mcp_config.json` (repo root): example MCP server definitions for the Python runtime (not Codex CLI’s `config.toml` format).
- `scripts/*.py`: CLI-oriented workflows that call MCP tools via the runtime harness. Many scripts read API keys from env or `~/.claude/.env`.

### Project setup / install scripts (Claude-biased)

- `install-global.sh`: installs everything into `~/.claude/*` (skills/agents/rules/hooks/scripts/plugins/settings.json) and installs the Python runtime as a global `uv tool`.
- `init-project.sh`: initializes a project with:
  - `thoughts/ledgers`, `thoughts/shared/{handoffs,plans}`, `.claude/cache/artifact-index/`
  - creates SQLite db at `.claude/cache/artifact-index/context.db` (if schema present)
  - updates `.gitignore` to ignore `.claude/cache/`

## Repo signals that matter for a Codex CLI port

### Path + naming mismatches to fix/plan for

- `.gitignore` ignores `CONTINUITY_CLAUDE-*` (ledger files) and `thoughts/` (except `thoughts/shared/*`).
- Several docs and scripts hardcode `.claude/…`:
  - DB default path: `.claude/cache/artifact-index/context.db` in `scripts/artifact_index.py`, `scripts/artifact_query.py`, `scripts/artifact_mark.py`, and the TS hooks.
  - Global env path: `~/.claude/.env` is referenced by multiple scripts.
  - Global MCP config: `~/.claude/mcp_config.json` in the runtime.
- `.agent/PLANS.md` references helper scripts (`scripts/new_execplan.py`, `scripts/archive_execplan.py`) that are not currently present in `scripts/`.
- Several docs reference a `docs/` directory that does not exist in this repo snapshot.

### Test + tooling baseline

- Python tests exist (`pytest`) under `tests/` and cover:
  - MCP client manager behavior (`tests/unit/test_mcp_client.py`)
  - wrapper/schema generation (`tests/unit/test_generate_wrappers.py`, etc.)
  - artifact index/query (`tests/test_artifact_index.py`, `tests/test_artifact_query.py`)

