# Port Continuous-Codex to Codex CLI (skills + continuity without Claude hooks)

This ExecPlan is a living document. Keep `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` up to date.

## Purpose / Big Picture

Port this repository from a **Claude Code–first continuity kit** (hooks/agents/plugins under `.claude/`) into a **Codex CLI–native kit** that preserves session state via **ledgers + handoffs**, and exposes the workflows as **Codex skills** under `.codex/skills/` (with optional installer scripts).

Success means:
- Running `codex` inside a project that uses this kit surfaces repo skills (via `/skills` or `$skill-name`).
- A user can reliably **start fresh chats** (or use `/new`) without losing fidelity, by loading a ledger/handoff from disk (no hook automation required).
- The SQLite artifact index works with Codex-era paths (prefer `.codex/cache/...`), and existing scripts remain usable (back-compat where reasonable).

## Progress

- [x] (2025-12-26) Repo + Codex CLI research captured in artifacts:
  - `.agent/execplans/artifacts/2025-12-26_port-to-codex-cli/internal-grounding.md`
  - `.agent/execplans/artifacts/2025-12-26_port-to-codex-cli/external-research.md`
- [ ] (YYYY-MM-DD HH:MM) Create repo-scoped Codex skills in `./.codex/skills/` (continuity + artifact index).
- [ ] (YYYY-MM-DD HH:MM) Update Python scripts to prefer `.codex/cache/...` and `~/.codex/...` (with compatibility).
- [ ] (YYYY-MM-DD HH:MM) Add Codex-friendly project init + optional global installer.
- [ ] (YYYY-MM-DD HH:MM) Update docs for Codex CLI usage (keep Claude docs as legacy/optional).
- [ ] (YYYY-MM-DD HH:MM) Run tests + manual smoke checks for skills + scripts.

## Surprises & Discoveries

- This repo contains a full Claude Code hook/agent system under `.claude/`, but **no `.codex/` directory yet**.
- `.gitignore` currently ignores `CONTINUITY_CLAUDE-*` and all of `thoughts/` except `thoughts/shared/*`. Ledger tracking statements in some docs/scripts appear outdated.
- `.agent/execplans/README.md` references helper scripts (`scripts/new_execplan.py`, `scripts/archive_execplan.py`) that are not present.
- Codex CLI skills are **repo-scoped via `.codex/skills`** and support explicit invocation (`/skills` or `$skill`) and implicit invocation by description (Codex skills docs).

## Decision Log

- Decision: Port as **dual-mode**: keep `.claude/` (Claude Code support) but add `.codex/` (Codex CLI support) rather than deleting Claude assets.
  - Rationale: minimizes breakage; allows incremental transition; avoids losing existing value.
  - Date/Author: 2025-12-26 / agent

- Decision: For Codex continuity artifacts, standardize on **`.codex/cache/...`** (project-local) while supporting legacy `.claude/cache/...` where needed.
  - Rationale: aligns with Codex’s `.codex/` project layering and avoids mixing Claude-specific state with Codex-native state.
  - Date/Author: 2025-12-26 / agent

- Decision: Introduce a Codex ledger prefix `CONTINUITY_CODEX-*.md` (preferred) while optionally falling back to `CONTINUITY_CLAUDE-*.md` for migration.
  - Rationale: avoids ambiguity and lets both tools coexist; simplifies `.gitignore` and skill logic.
  - Date/Author: 2025-12-26 / agent

<!-- AGENT: Confirm naming preference: should ledgers/handoffs keep “CLAUDE” for compatibility, or fully rename to “CODEX” everywhere (including docs/templates)? -->

## Outcomes & Retrospective

_To be filled after implementation._

## Context and Orientation

### Key repo paths (current)

- Claude Code integration:
  - `.claude/settings.json` (hook registration)
  - `.claude/hooks/` (TS hooks; continuity logic is here today)
  - `.claude/skills/`, `.claude/agents/`, `.claude/plugins/`, `.claude/rules/`
- Continuity data:
  - Ledger: `thoughts/ledgers/CONTINUITY_CLAUDE-*.md` (currently referenced; ignored by `.gitignore`)
  - Handoffs: `thoughts/shared/handoffs/<stream>/*.md` (tracked)
  - Plans: `thoughts/shared/plans/*.md` (tracked)
- Artifact index:
  - Default DB (today): `.claude/cache/artifact-index/context.db`
  - Schema: `scripts/artifact_schema.sql`
  - Scripts: `scripts/artifact_index.py`, `scripts/artifact_query.py`, `scripts/artifact_mark.py`
- MCP runtime:
  - `src/runtime/mcp_client.py` (merges `.mcp.json`/`mcp_config.json` with legacy `~/.claude/mcp_config.json`)
  - `src/runtime/harness.py` (exec harness)
  - `mcp_config.json` (repo JSON example)

### Codex CLI primitives we will port to

- Skills (experimental): directories with `SKILL.md` under `.codex/skills` (repo scope) or `~/.codex/skills` (user scope). Skills support `$skill-name` explicit invocation and implicit selection.
  - Ref: `https://developers.openai.com/codex/skills`
- AGENTS.md memory layering: global `~/.codex/AGENTS.md` + repo `AGENTS.md` chain.
  - Ref: `https://raw.githubusercontent.com/openai/codex/main/docs/agents_md.md`
- Custom prompts: `~/.codex/prompts/*.md` (optional; not repo-scoped).
  - Ref: `https://raw.githubusercontent.com/openai/codex/main/docs/prompts.md`
- Codex slash commands: `/new`, `/compact`, `/status`, `/skills`, etc.
  - Ref: `https://raw.githubusercontent.com/openai/codex/main/docs/slash_commands.md`

## Plan of Work

### Milestone 1 — Create repo-scoped Codex skills (`.codex/skills/`)

Add a new repo directory: `./.codex/skills/` (tracked). Create a minimal, high-signal set of skills that replaces the Claude hook automation with explicit, user-invoked workflows.

Proposed initial skill set:

1) `./.codex/skills/continuity-ledger/SKILL.md`
   - Codex-native version of `.claude/skills/continuity_ledger/SKILL.md`
   - Writes/updates `thoughts/ledgers/CONTINUITY_CODEX-<stream>.md`
   - Includes a strict template + “one Now item” rule + UNCONFIRMED rule

2) `./.codex/skills/create-handoff/SKILL.md`
   - Codex-native version of `.claude/skills/create_handoff/SKILL.md`
   - Writes `thoughts/shared/handoffs/<stream>/YYYY-MM-DD_HH-MM-SS_description.md`
   - After writing, runs `uv run python scripts/artifact_index.py --file <handoff>` and optionally `scripts/artifact_mark.py` for outcome
   - Replaces “AskUserQuestion tool” references with plain instructions (“ask the user to pick outcome”) since Codex doesn’t expose Claude’s AskUserQuestion tool

3) `./.codex/skills/resume-handoff/SKILL.md`
   - Codex-native version of `.claude/skills/resume_handoff/SKILL.md`
   - Reads a target handoff file, then reads referenced artifacts (plans/research/files), and proposes next actions.

4) `./.codex/skills/artifact-search/SKILL.md` (optional but useful)
   - Wraps `uv run python scripts/artifact_query.py --query "..."` and documents common queries.

5) `./.codex/skills/init-project/SKILL.md`
   - Runs the new Codex init script (Milestone 3) to create `thoughts/*` + `.codex/cache/artifact-index/`.

Implementation notes:
- Codex skills require YAML frontmatter with `name:` and `description:` (and optionally `metadata.short-description`). Keep descriptions “selection-friendly” (Codex matches on them).
- Prefer **skills** over prompts for portability, since prompts are only loaded from `~/.codex/prompts`.

### Milestone 2 — Make scripts Codex-path-native (keep compatibility)

Update scripts that currently hardcode `.claude/…` or `~/.claude/…`:

1) Artifact DB path:
- Update `scripts/artifact_index.py`, `scripts/artifact_query.py`, `scripts/artifact_mark.py` to default to:
  - `.codex/cache/artifact-index/context.db`
  - fallback to `.claude/cache/artifact-index/context.db` if present (migration mode)
  - still accept `--db PATH` to override

2) Global `.env` lookup:
- Update scripts that look for `~/.claude/.env` (e.g. `scripts/perplexity_search.py`, `scripts/firecrawl_scrape.py`, `scripts/nia_docs.py`) to:
  - prefer environment variables
  - then project `.env`
  - then `~/.codex/.env` (if we decide to support a Codex-global env file)
  - finally legacy `~/.claude/.env` (for existing users)

<!-- AGENT: Do we want to standardize on `~/.codex/.env` as the “global env file” for this kit, or drop global `.env` support entirely and require project `.env` + exported env vars? -->

3) MCP runtime global config:
- Update `src/runtime/mcp_client.py` (and `src/runtime/generate_wrappers.py` if needed) to add Codex-native global config support:
  - Prefer project `.mcp.json` / `mcp_config.json` (existing)
  - If no project config, attempt to read `~/.codex/config.toml` and extract `[mcp_servers]` into the runtime’s `McpConfig` shape (use `tomllib`, Python 3.11 stdlib)
  - Keep legacy fallback to `~/.claude/mcp_config.json` (optional)

Acceptance for this milestone:
- `uv run pytest` still passes.
- Running `uv run python scripts/artifact_index.py --all` creates/uses the DB under `.codex/cache/...` by default.

### Milestone 3 — Codex-friendly project initialization + optional global install

Add Codex-native setup scripts without overwriting user Codex config:

1) Add `scripts/init-project-codex.sh` (or rename + keep shim)
- Creates:
  - `thoughts/ledgers/`
  - `thoughts/shared/{handoffs,plans,research}/`
  - `.codex/cache/artifact-index/` + initializes DB from `scripts/artifact_schema.sql`
- Adds `.codex/cache/` to `.gitignore` if desired (or document that repo already ignores it).

2) Add `install-codex-global.sh` (optional, safe-by-default)
- Installs skills into `~/.codex/skills/<skill-name>` by copying from this repo’s `.codex/skills/`
- Optionally installs prompts into `~/.codex/prompts/` (if we ship any)
- Never overwrites `~/.codex/config.toml` automatically; instead prints a “paste this snippet” section for `[mcp_servers]` and `features.skills=true`.
- Creates timestamped backups before overwriting any target directory.

Acceptance:
- A fresh clone + `bash scripts/init-project-codex.sh` creates the expected folders + DB.
- Running `codex` in the repo shows skills available (with `features.skills=true`).

### Milestone 4 — Documentation and migration story

Update docs so a Codex CLI user can adopt the kit without Claude knowledge:

1) Update `README.md` (or add `CODEX.md`) with:
- “How to use with Codex CLI”
  - enable skills (`features.skills=true`)
  - where skills live (`.codex/skills`)
  - recommended workflow: `$continuity-ledger` before `/new` or before `/compact`, `$create-handoff` when pausing work
  - how to resume: `$resume-handoff` or `$continuity-ledger` then continue
- “What’s Claude-only” section (hooks/agents/plugins) if we keep `.claude/`.

2) Update `AGENTS.md` to include Codex CLI-specific guidance:
- prefer repo skills for continuity
- reference `.agent/PLANS.md` ExecPlan format (already present)

3) Optional: add migration notes:
- how to rename existing `CONTINUITY_CLAUDE-*` → `CONTINUITY_CODEX-*` (or how the new skills handle both)

Acceptance:
- Docs contain copy/paste commands and exact paths.
- No broken references to missing `docs/` directories (either create them or remove references).

### Milestone 5 — Validation + smoke tests

Run:
- `uv sync`
- `uv run pytest`

Manual smoke tests (Codex):
1) Ensure skills are enabled:
   - `codex` → `/experimental` → enable Skills (or set `[features].skills=true` in `~/.codex/config.toml`)
2) In repo root, run:
   - `bash scripts/init-project-codex.sh`
3) Start Codex and invoke:
   - `$continuity-ledger` (create ledger)
   - `$create-handoff` (create handoff, index it)
   - `$resume-handoff thoughts/shared/handoffs/<stream>/<file>.md` (resume)
4) Verify artifact DB contains the handoff:
   - `uv run python scripts/artifact_query.py --type handoffs --limit 5` and confirm it shows up.

## Concrete Steps

> These are the implementation commands for the engineer executing this plan.

### Repo prep

```bash
cd /path/to/Continuous-Codex
uv sync
```

### Milestone 1: Add Codex skills

```bash
mkdir -p .codex/skills
mkdir -p .codex/skills/continuity-ledger
mkdir -p .codex/skills/create-handoff
mkdir -p .codex/skills/resume-handoff
mkdir -p .codex/skills/init-project
# (optional)
mkdir -p .codex/skills/artifact-search
```

Populate each `SKILL.md` with required frontmatter:
```yaml
---
name: continuity-ledger
description: Create/update a continuity ledger for Codex sessions (survives /new and avoids /compact)
metadata:
  short-description: Update ledger before starting a fresh chat
---
```

### Milestone 2: Update scripts + runtime paths

Suggested approach:
- Add a small shared helper in `scripts/` (or `src/runtime/`) for:
  - resolving project cache dir: prefer `.codex/cache`, fallback `.claude/cache`
  - resolving global env: prefer env → project `.env` → `~/.codex/.env` → `~/.claude/.env`

Then update:
```bash
rg -n \"\\.claude/cache\" scripts src
rg -n \"\\.claude/\\.env|~/.claude/.env\" scripts src
rg -n \"~/.claude/mcp_config.json\" src/runtime
```

### Milestone 5: Run tests

```bash
uv run pytest
```

## Validation and Acceptance

Functional acceptance criteria:

- Codex skill discovery:
  - When running `codex` in repo root with skills enabled, `/skills` shows the new repo skills.
- Continuity workflow:
  - `$continuity-ledger` creates/updates `thoughts/ledgers/CONTINUITY_CODEX-*.md`.
  - `$create-handoff` creates a handoff under `thoughts/shared/handoffs/<stream>/...` and indexes it into `.codex/cache/artifact-index/context.db`.
  - `$resume-handoff` reads the handoff + linked artifacts and produces a concrete next-step list.
- Artifact index:
  - `uv run python scripts/artifact_index.py --all` uses `.codex/cache/artifact-index/context.db` by default (or clearly reports fallback).
- Test suite:
  - `uv run pytest` passes.

## Idempotence and Recovery

- All new setup scripts should be safe to re-run:
  - `mkdir -p` for directories
  - SQLite schema init should be “create if not exists” (current schema already uses idempotent DDL patterns; verify).
- Any global install script must:
  - create timestamped backups of `~/.codex/skills/<skill>` before overwrite
  - never edit `~/.codex/config.toml` without an explicit `--yes`/`--force` style flag

## Artifacts and Notes

- Internal grounding: `.agent/execplans/artifacts/2025-12-26_port-to-codex-cli/internal-grounding.md`
- External research: `.agent/execplans/artifacts/2025-12-26_port-to-codex-cli/external-research.md`

## Interfaces and Dependencies

- Requires: Codex CLI with skills enabled (`[features].skills=true`).
- Requires: Python 3.11+ (repo already specifies `>=3.11`); `uv` recommended (`uv sync`).
- Optional: MCP servers (Codex-native via `~/.codex/config.toml` `[mcp_servers]`), plus the repo’s Python MCP runtime for script-based tool execution.
