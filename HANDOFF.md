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

## Local dev server (review & testing)

The installed `configure` binary serves the **last installed version**, not live repo changes. To test edits in `configure.py` without reinstalling:

```bash
# Kill the service (frees port 4827)
sudo systemctl stop configure      # Linux/WSL2
# or: launchctl stop com.oculus.configure   # macOS

# Run repo version directly — opens browser automatically
cd ~/repos/oculus-configs
python3 configure.py

# Ctrl+C to stop, then restart service when done
sudo systemctl start configure
```

**Alt: run on a spare port** (leaves service running)

```bash
# One-liner — temp copy on 4828, no browser pop
sed 's/PORT = 4827/PORT = 4828/' configure.py > /tmp/configure_dev.py
python3 /tmp/configure_dev.py
# open http://localhost:4828 manually
```

**Tests** (no server needed):

```bash
python3 tests/test_configure.py        # 65 tests, stdlib only, ~0.25s
```

**After UI changes** — reinstall binary so `configure` picks them up:

```bash
cp configure.py ~/.local/bin/configure
chmod +x ~/.local/bin/configure
sudo systemctl restart configure
```

---

## Near-term items

- [ ] Set GitHub PAT via MCP Setup tab
- [x] **CCC integration** — complete
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

## Resumption prompt (this repo)

> "Resume oculus-configs (5b61a0c). Repo is clean — 65 tests, glass/aurora GUI, 9-section install.sh covering Claude/Codex/Gemini CLI. README and DECISIONS.md are current (ADR-010). CCC integration is complete. Check Near-term items for what's left."
