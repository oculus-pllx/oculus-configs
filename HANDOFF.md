# Session Handoff — oculus-configs

**Date**: 2026-05-28
**Branch**: main
**Last commit**: 5b61a0c fix: correct aurora theme accent-glow value to match spec

---

## What exists now

`configure.py` is complete and pushed. `install.sh` does full setup in one shot.

- Python 3 stdlib HTTP server on port 4827
- Glass/aurora dark SPA — top nav bar, frosted glass, 3-theme picker (True Aurora, Sky Cyan, Violet)
- 7 sections: Dashboard, Project Commander, CLAUDE.md (Wizard + Raw Edit), MCP Setup, Plugins, Templates, New Project
- **65 unit tests** (`python3 tests/test_configure.py`)

### Install & Service

`bash install.sh` does 9 sections:

1. Global CLAUDE.md → ~/.claude/CLAUDE.md
2. rules/ → ~/.claude/rules/
3. MCP config template → ~/.claude/claude_desktop_config.json
4. Starter template → ~/Templates/claude-code-starter/
5. configure binary → ~/.local/bin/configure
6. repo_path → ~/.claude/settings.json
7. Service setup — systemd (Linux/WSL2) or launchd (macOS)
8. Codex CLI setup — AGENTS.md + 8 skills → ~/.codex/
9. Gemini CLI setup — GEMINI.md + 8 skills → ~/.gemini/

### GUI Redesign (completed 2026-05-22)

Commits: `4e3a556` (spec + themes.md) → `3b92a58` (full redesign) → `5b61a0c` (aurora glow fix)

- Old: 200px left sidebar, flat `#0f0f0f`, hard-coded `#2563eb` accent
- New: top nav bar, `body::before` aurora radial gradients, `--accent` CSS var, 3 theme swatches
- Theme data sheet at `docs/themes.md` — portable to any dark web project

### Self-Update (Dashboard)

- `GET /api/update/check` — git fetch + rev-list count
- `POST /api/update/apply` — pull → copy binary → restart service

### Repo structure

```
oculus-configs/
├── configure.py          ← local web UI (port 4827), glass/aurora
├── install.sh            ← one-shot install (9 sections)
├── claude/               ← CLAUDE.md, mcp.json, rules/
├── codex/                ← AGENTS.md + 8 skills → ~/.codex/
├── gemini/               ← GEMINI.md + 8 skills → ~/.gemini/
├── templates/
│   └── claude-code-starter/
│       ├── CLAUDE.md
│       ├── mcp.json
│       └── docs/DECISIONS.md
├── tests/
│   └── test_configure.py ← 65 tests
└── docs/
    ├── DECISIONS.md      ← ADR-001 through ADR-010
    ├── themes.md         ← Aurora theme system (portable)
    ├── specs/
    └── plans/
```

---

## Near-term items

- [ ] Set GitHub PAT via MCP Setup tab
- [ ] **CCC integration** — see below
- [x] Gemini CLI support
- [x] Add mcp.json to templates/claude-code-starter/
- [x] Fix apply_update to restart systemd after binary copy
- [x] File manager: show hidden folders + keyboard shortcuts
- [x] Codex CLI Superpowers port
- [x] Glass/aurora GUI redesign with 3-theme picker

---

## On the new machine

```bash
git clone git@github.com:oculus-pllx/oculus-configs.git ~/repos/oculus-configs
cd ~/repos/oculus-configs
./install.sh
configure   # verify the GUI opens at http://localhost:4827
python3 tests/test_configure.py   # should show 65 tests OK
```

---

## CCC Integration (next major task)

**Repo**: https://github.com/oculus-pllx/CCC
**Work in**: ~/repos/CCC (clone it there if not present)

oculus-configs is ready to be consumed by CCC as a provisioning step. CCC currently embeds CLAUDE.md as a heredoc (line ~619, step 18) and creates `~/.claude/skills/` but doesn't populate it.

**What the integration needs:**
1. New provisioning step: clone oculus-configs + run `./install.sh` inside the container
2. Remove the inline CLAUDE.md heredoc (replaced by install.sh)
3. Open port 4827 in the firewall step (configure UI, alongside code-server on 8080)
4. Add configure UI entry to the MOTD

**Resumption prompt for CCC session:**
> "Resume CCC integration. We want to add oculus-configs (https://github.com/oculus-pllx/CCC) as a provisioning step in claude-code-commander.sh. During LXC setup, CCC should clone oculus-configs into the container and run install.sh, replacing the embedded CLAUDE.md heredoc (step 18, line ~619) with the one from oculus-configs. configure.py then runs as a systemd service on port 4827 alongside code-server (8080). Need to: (1) add provisioning step to clone + run install.sh, (2) remove the inline CLAUDE.md heredoc, (3) open port 4827 in the firewall step, (4) add configure UI to the MOTD. Start with brainstorming."

---

## Resumption prompt (this repo)

> "Resume oculus-configs (5b61a0c). Repo is clean — 65 tests, glass/aurora GUI, 9-section install.sh covering Claude/Codex/Gemini CLI. README and DECISIONS.md are current (ADR-010). CCC integration is the active next task (see HANDOFF.md). If staying in this repo, check Near-term items."
