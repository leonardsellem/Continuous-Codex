# External Research — Codex CLI (current) vs Claude Code

Timestamp: 2025-12-26

This summarizes **current Codex CLI capabilities** (observed locally + upstream docs) and key **gaps vs Claude Code** that matter when porting this repo.

## Ground truth: local Codex CLI inspection

- Installed version: `codex-cli 0.77.0` (`codex --version`)
- Feature flags visible via `codex features list` (local):
  - Stable: `undo`, `parallel`, `view_image_tool`, `shell_tool`, `warnings`, `web_search_request`
  - Beta: `unified_exec`
  - Experimental: `apply_patch_freeform`, `exec_policy`, `remote_compaction`, `skills`, `tui2`
- Key subcommands in `codex --help` (local):
  - Interactive: `codex` (TUI)
  - Automation: `codex exec …`
  - Session: `codex resume …`
  - Code review: `codex review …`
  - Patch application: `codex apply`
  - MCP: `codex mcp …` / `codex mcp-server`
  - Sandbox helper: `codex sandbox …`

## Codex CLI capabilities relevant to this repo

### 1) Session management + context controls

Codex supports:
- Resuming sessions: `codex resume` (picker), `codex resume --last`, or `codex resume <SESSION_ID>` (session ids live under `~/.codex/sessions/`).  
  Source: `https://raw.githubusercontent.com/openai/codex/main/docs/getting-started.md`
- Built-in slash commands:
  - `/new` (start a new chat)
  - `/compact` (summarize conversation to avoid hitting context limit)
  - `/status` (shows configuration + token usage)
  - `/resume` (resume an old chat)
  Source: `https://raw.githubusercontent.com/openai/codex/main/docs/slash_commands.md`

Implication for port: Codex has **native compaction** (`/compact`) similar to Claude Code compaction; this repo’s “ledger + fresh context” approach is still useful, but **Codex does not provide Claude-style lifecycle hooks** to enforce it automatically.

### 2) AGENTS.md “memory” model (Codex-native)

Codex ingests global + per-repo `AGENTS.md` files **top-down**:
1. `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md`
2. For each directory from repo root → working dir: `AGENTS.override.md` else `AGENTS.md` (plus configurable fallback names)

Source:  
- `https://raw.githubusercontent.com/openai/codex/main/docs/getting-started.md#memory-with-agentsmd`  
- `https://raw.githubusercontent.com/openai/codex/main/docs/agents_md.md`

Implication for port: we should move Claude “rules” and “operational style” into **AGENTS.md-scoped guidance**, rather than Claude Code rules/hooks.

### 3) Skills system (Codex CLI: experimental, progressive disclosure)

Codex “skills” are **directories** containing a required `SKILL.md` (plus optional `scripts/`, `references/`, `assets/`), and are loaded with **progressive disclosure**:
- At startup Codex loads only skill `name` + `description`.
- Skills can be used via:
  - Explicit invocation: `/skills` or typing `$` to mention a skill.
  - Implicit invocation: Codex chooses a skill when the task matches the skill description.

Source: `https://developers.openai.com/codex/skills` (notably the “progressive disclosure” + explicit/implicit invocation sections).

Supported skill locations + precedence (high → low):
- Repo scopes:
  - `$CWD/.codex/skills`
  - `$CWD/../.codex/skills` (within a git repo)
  - `$REPO_ROOT/.codex/skills`
- User scope: `$CODEX_HOME/skills` (default `~/.codex/skills`)
- Admin scope: `/etc/codex/skills`
- System scope: bundled with Codex

Source: `https://developers.openai.com/codex/skills` (“Where to save skills” table).

Skill metadata format (minimum):
```yaml
---
name: skill-name
description: Description that helps Codex select the skill
metadata:
  short-description: Optional user-facing description
---
```
Source: `https://developers.openai.com/codex/skills` (SKILL.md example).

Implication for port:
- This repo should add **repo-scoped skills** under `./.codex/skills/...`.
- Existing `.claude/skills/*/SKILL.md` files generally need to be **converted** (add `name:`, update wording, remove Claude-only tooling references).
- The prior Claude-only “skill-rules.json” keyword matcher/hook is unnecessary; Codex has implicit skill selection, and explicit `$skill` invocation.

### 4) Custom prompts (Codex CLI)

Codex supports reusable slash commands via prompt files in `$CODEX_HOME/prompts/*.md` (default `~/.codex/prompts`). Prompts support positional and named placeholders.

Source: `https://raw.githubusercontent.com/openai/codex/main/docs/prompts.md`

Implication for port:
- Repo-distributed continuity actions should be implemented as **skills** (portable, repo-local).
- Optional global quality-of-life commands can be shipped as prompts, but require installation into `~/.codex/prompts`.

### 5) Web search

Codex exposes a native `web_search` tool when started with `--search` (off by default).
Source: `codex --help` and `codex resume --help` (local), plus getting-started docs.

Implication for port:
- We can drop/optionalize Perplexity MCP usage in favor of native web search for “current best practices” validation steps.

### 6) MCP integration (Codex-native)

Codex can connect to MCP servers configured in `~/.codex/config.toml` under `[mcp_servers.<name>]`.
Source: `https://raw.githubusercontent.com/openai/codex/main/docs/config.md#mcp-integration`

Codex also provides:
- `codex mcp add/list/get/remove/login/logout`
Source: same config doc section.

Implication for port:
- This repo’s Python MCP runtime currently reads `.mcp.json`/`mcp_config.json` plus `~/.claude/mcp_config.json`. For Codex CLI parity, we should either:
  - (A) teach the Python runtime to also read Codex’s `~/.codex/config.toml` `[mcp_servers]`, or
  - (B) keep the existing JSON configs but add docs/scripts to “sync” definitions into Codex config.

### 7) Sandbox + approvals + execpolicy

Codex includes:
- sandbox modes: `read-only`, `workspace-write`, `danger-full-access`
- approval policies: `untrusted`, `on-failure`, `on-request`, `never`
Source: `https://raw.githubusercontent.com/openai/codex/main/docs/sandbox.md`

Codex also supports rules-based execpolicy:
- `.rules` files under `~/.codex/rules` with `prefix_rule(...)`
Source: `https://raw.githubusercontent.com/openai/codex/main/docs/execpolicy.md`

Implication for port:
- Claude “rules” should become AGENTS.md guidance; Codex command safety should be handled via execpolicy where needed.

## Key limitations vs Claude Code (port blockers)

Claude Code capabilities heavily used by this repo that Codex CLI **does not** currently provide:

1) **Lifecycle hooks** (SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / PreCompact / etc.)  
   - This repo depends on hooks to auto-load ledgers, auto-write handoffs, suggest skills, and index artifacts on every Write.
   - Codex CLI has **slash commands** but no equivalent “run a script on every tool call” hook system.

2) **First-class sub-agents with isolated context windows (Claude “agents”)**  
   - This repo’s plan-agent / validate-agent / implement_plan orchestration is built around Claude subagents.
   - Codex CLI does not have the same native agent definition format; the closest substitutes are:
     - `codex exec …` (non-interactive runs that can be treated like “task agents”), and/or
     - using Codex as an MCP server (`codex mcp-server`) from an external orchestrator.

3) **Plugin system (e.g., Braintrust tracing hooks)**  
   - Codex has built-in logs + optional OpenTelemetry export, but not the same plugin hook points.

Net: the Codex port must replace “automatic” hook behavior with **skills + scripts + explicit workflows** (user-initiated), or with a **wrapper launcher** that standardizes “start session / save ledger / create handoff / start new session” flows.

