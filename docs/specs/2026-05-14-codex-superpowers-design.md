# Codex CLI — Superpowers Skills Port

**Date**: 2026-05-14  
**Status**: Approved  
**Scope**: Bring Superpowers-equivalent workflow discipline to Codex CLI

---

## Goal

Port the 8 core Superpowers skills and a global config to Codex CLI so that
sessions have the same brainstorm-first, test-first, verify-before-done discipline
as Claude Code sessions. No UI changes to configure.py this iteration.

---

## Directory Structure

### In repo (`oculus-configs/codex/`)

```
codex/
├── AGENTS.md
└── skills/
    ├── brainstorming/
    │   └── SKILL.md
    ├── systematic-debugging/
    │   └── SKILL.md
    ├── test-driven-development/
    │   └── SKILL.md
    ├── requesting-code-review/
    │   └── SKILL.md
    ├── receiving-code-review/
    │   └── SKILL.md
    ├── writing-plans/
    │   └── SKILL.md
    ├── verification-before-completion/
    │   └── SKILL.md
    └── finishing-a-development-branch/
        └── SKILL.md
```

### Installed to (`~/.codex/`)

Same layout. `install.sh` copies `codex/AGENTS.md` → `~/.codex/AGENTS.md` and
`codex/skills/` → `~/.codex/skills/`. Existing `AGENTS.md` is backed up, not
overwritten silently.

---

## AGENTS.md

Global config file. Mirrors `claude/CLAUDE.md` in structure and intent.

### Sections

1. **Tool mapping block** — single global translation table so skill files don't
   need individual tool-name adaptations:
   - `Read/Write/Edit` → use shell commands (cat, write directly)
   - `TodoWrite` → maintain checklist at `/tmp/codex-tasks.md`
   - `Skill` tool invocation → `cat ~/.codex/skills/<name>/SKILL.md` and follow it
   - `Task` subagent dispatch → noted as unsupported, skip those steps

2. **Workflow triggers** — mirrors the "when to invoke each skill" rules from
   `claude/rules/plugin-usage.md`:
   - New feature / non-trivial task → brainstorming
   - Before writing application code → test-driven-development
   - Bug present for >10 min → systematic-debugging
   - Before claiming done / committing → verification-before-completion
   - Implementation complete → finishing-a-development-branch
   - Receiving review feedback → receiving-code-review

3. **Code quality rules** — same content as `claude/rules/code-quality.md`
   (coverage thresholds, no console.log, no hardcoded secrets, parameterized
   queries, single-purpose functions).

4. **Session discipline** — one task per session, commit frequently, update
   HANDOFF.md at session end.

---

## Skills

### Source

Copied verbatim from Superpowers 5.1.0 with minimal adaptations. The skill
prose is tool-agnostic; only invocation references are Codex-specific.

### Skills included

| Skill | Trigger |
|---|---|
| brainstorming | Before any new feature or behavior change |
| systematic-debugging | When stuck on a bug |
| test-driven-development | Before writing implementation code |
| requesting-code-review | Before merging / marking done |
| receiving-code-review | When acting on review feedback |
| writing-plans | After design is approved, before coding |
| verification-before-completion | Before any "done" claim or commit |
| finishing-a-development-branch | When implementation is complete |

### Skills excluded

| Skill | Reason |
|---|---|
| using-superpowers | Replaced by AGENTS.md itself |
| using-git-worktrees | Claude Code worktree API, no Codex equivalent |
| dispatching-parallel-agents | Task tool subagent dispatch not in Codex |
| executing-plans | Depends on Task tool subagent dispatch |
| subagent-driven-development | Depends on Task tool subagent dispatch |
| writing-skills | Meta-skill for Claude Code plugin authoring |

### Lazy loading

Skills are NOT `@`-included in AGENTS.md. That would load all skill content
into every session. Instead, AGENTS.md instructs Codex to read the relevant
skill file when the trigger condition is met. Codex uses `cat` to read the
file on demand — equivalent to Claude Code's `Skill` tool.

---

## install.sh Changes

New section 8: **Codex CLI setup**

```
if codex is in PATH:
  backup ~/.codex/AGENTS.md → ~/.codex/AGENTS.md.bak (if exists)
  copy codex/AGENTS.md → ~/.codex/AGENTS.md
  copy codex/skills/* → ~/.codex/skills/
  print [ok] lines
else:
  print [skip] codex not found
```

Section is non-fatal — if Codex is not installed the rest of install.sh
continues normally.

---

## Out of Scope

- configure.py Codex tab (separate task)
- Gemini CLI support (separate task, post-Codex)
- `apply_update` syncing Codex skills (separate task)
- Writing new skills not already in Superpowers
