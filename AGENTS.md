# AGENTS.md

This file is for AI coding agents (Codex, etc.) and humans collaborating with them.
Keep it **short, specific, and actionable**.

## Project

**Name:** Continuous Codex

**What is this?** Context management for Codex. Hooks maintain state via ledgers and handoffs. MCP execution without context pollution. Agent orchestration with isolated context windows.

## Working style for this repo

- Default to **small, finishable steps**.
- Be explicit about **assumptions**, **open questions**, and **what you changed**.
- Prefer **safe, reversible edits** over big-bang refactors.
- When in doubt, propose **2–3 options**, pick one, then execute.

## ExecPlans

We use **ExecPlans** for complex work (multi-hour features, risky refactors, or anything with real unknowns).

- ExecPlan rules live in: **`.agent/PLANS.md`**
- Create new ExecPlans in: **`.agent/execplans/`**
- Completed ExecPlans + their artifacts get moved to: **`.agent/execplans/archive/`**

**Use an ExecPlan when:**
- the task will take > ~45 minutes, OR
- it touches > ~3 files / multiple subsystems, OR
- there are unknowns / tradeoffs to resolve, OR
- you want a crisp “definition of done” with validation steps.

**ExecPlan lifecycle (practical):**
1. Draft the ExecPlan (self-contained; includes commands + acceptance checks).
2. Implement milestone-by-milestone, keeping the plan updated.
3. Save supporting outputs in `.agent/execplans/artifacts/<plan-id>/`.
4. Archive when done.

## Debugging journal

Use **`.agent/DEBUG.md`** as a lightweight debugging notebook:
- Repro steps
- Hypotheses
- Experiments (time-stamped)
- Fix + regression tests

By default, `.agent/DEBUG.md` is gitignored (local-only).

## Repo-scoped Codex skills

Repo skills live in **`.codex/skills/`**. Keep them:
- narrow (one workflow per skill)
- heavily templated (copy/paste scripts and checklists)
- safe by default

## Commit messages

We prefer **Conventional Commits** (e.g., `feat: ...`, `fix: ...`, `refactor: ...`).

This repo includes an optional **AI commit-message hook**:
- Versioned hook lives in `.githooks/prepare-commit-msg`
- It can call `scripts/ai_commit_message.py`

**Safety note:** The hook may send staged diffs to the model. Do not stage secrets.

## “Done” means

A change is done when:
- tests / checks pass (or you explain what you ran)
- the behavior is demonstrably correct (example, screenshot, transcript, etc.)
- docs are updated if the change affects how to use the project
