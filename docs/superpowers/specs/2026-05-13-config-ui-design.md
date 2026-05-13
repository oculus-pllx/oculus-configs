# Design Spec: oculus-configs Local Config UI

**Date**: 2026-05-13  
**Status**: Approved  
**Scope**: Single-file Python web UI for managing Claude Code configs locally

---

## Problem

Editing `~/.claude/CLAUDE.md`, MCP config, and plugin settings requires manual file editing. On WSL, macOS, and Linux this is friction for anyone not comfortable in a terminal. A local browser UI removes that friction and provides status visibility at a glance.

## Solution

A single `configure.py` (Python 3 stdlib only, no pip installs) that:
- Starts a local HTTP server on port **4827**
- Auto-opens the browser on launch
- Serves an embedded single-page UI
- Exposes a small REST API to read/write `~/.claude/` files

## Non-Goals

- No authentication (localhost only)
- No database
- No npm/pip dependencies
- Not a hosted service — local tool only
- CCC integration is out of scope (CCC will absorb the frontend separately)

## Architecture

```
configure.py
├── Python HTTP server (stdlib http.server)
├── Embedded HTML/CSS/JS (single string, no separate files)
└── REST API routes
    ├── GET  /api/status          → config health check
    ├── GET  /api/config/{file}   → read a config file
    ├── POST /api/config/{file}   → write a config file
    └── GET  /api/plugins         → read installed_plugins.json
```

**Why embedded HTML:** Keeps the tool as one file. `python3 configure.py` is the entire install. No assets to serve, no paths to manage.

## UI Sections

### 1. Dashboard
Landing page. Status grid showing green/yellow/red for:
- `~/.claude/CLAUDE.md`
- `~/.claude/rules/`
- MCP config (present + token set)
- `~/Templates/claude-code-starter/`
- Each installed plugin (enabled/disabled state)

### 2. CLAUDE.md Wizard
Form-based builder for `~/.claude/CLAUDE.md`:
- Checkboxes for active plugins
- Dropdowns for token discipline settings
- Text areas for custom workflow rules
- Live preview pane on the right
- Save button writes to `~/.claude/CLAUDE.md`

### 3. MCP Setup
- Token input field for GitHub (writes to `~/.claude/claude_desktop_config.json`)
- Toggle list of available MCP servers with token-cost annotations
- Each toggle adds/removes the server from the config

### 4. Plugins
- Table of installed plugins with enabled/disabled state
- Copy-paste install commands for missing plugins
- Enable/disable toggles write only to the `enabledPlugins` key in `~/.claude/settings.json` — no other keys touched

### 5. Templates
- View and edit `~/Templates/claude-code-starter/CLAUDE.md`
- View and edit `~/Templates/claude-code-starter/docs/DECISIONS.md`
- Save writes directly to the template files

## File Location

```
oculus-configs/
└── configure.py    ← single entry point
```

## Usage

```bash
python3 configure.py
# Server starts on http://localhost:4827
# Browser opens automatically
# Ctrl+C to stop
```

## Future / CCC Integration

The HTML/JS frontend can be extracted verbatim into CCC's management GUI. The Python REST API maps cleanly to whatever backend CCC uses. No coupling assumptions made here.
