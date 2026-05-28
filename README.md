# oculus-configs

Global AI CLI configurations for Claude Code, Codex, and Gemini CLI.
Drop-in setup for a fresh workstation — one install script, local web UI, ready to go.

## Quick Start

```bash
git clone git@github.com:oculus-pllx/oculus-configs.git
cd oculus-configs
./install.sh
configure   # opens http://localhost:4827 — glass/aurora GUI
```

Then in a Claude Code session:
```
/plugin install superpowers@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
/plugin install skill-creator@claude-plugins-official
```

## Structure

```
oculus-configs/
├── configure.py              # Local web UI (port 4827) — glass/aurora SPA
├── install.sh                # One-shot install (9 sections)
├── claude/                   # Claude Code configs → ~/.claude/
│   ├── CLAUDE.md             # Global rules (all projects)
│   ├── mcp.json              # MCP server config template
│   └── rules/
│       ├── code-quality.md   # Test thresholds, pre-commit checks
│       └── plugin-usage.md   # When to invoke which skill/plugin
├── codex/                    # Codex CLI configs → ~/.codex/
│   ├── AGENTS.md             # Global rules for Codex sessions
│   └── skills/               # 8 Superpowers-equivalent skills
├── gemini/                   # Gemini CLI configs → ~/.gemini/
│   ├── GEMINI.md             # Global rules + tool mapping
│   └── skills/               # 8 Superpowers-equivalent skills
├── templates/
│   └── claude-code-starter/  # Project template → ~/Templates/
│       ├── CLAUDE.md
│       ├── mcp.json
│       └── docs/DECISIONS.md
├── tests/
│   └── test_configure.py     # 65 unit tests
└── docs/
    ├── DECISIONS.md          # ADR-001 through ADR-010
    ├── themes.md             # Aurora theme system — portable CSS/JS data sheet
    ├── setup-guide.md        # Complete workstation setup (30 min)
    ├── quick-reference.md    # Cheat sheet
    ├── visual-workflows.md   # Flowcharts and decision trees
    └── project-templates.md  # Template files explained
```

## What Gets Installed

| Source | Destination | Purpose |
|--------|-------------|---------|
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | Global rules for all Claude sessions |
| `claude/rules/*.md` | `~/.claude/rules/` | Modular rule files |
| `claude/mcp.json` | `~/.claude/claude_desktop_config.json` | MCP server config (template) |
| `templates/claude-code-starter/` | `~/Templates/claude-code-starter/` | Project starter |
| `configure.py` | `~/.local/bin/configure` | Local web UI binary |
| `codex/AGENTS.md` | `~/.codex/AGENTS.md` | Codex global rules |
| `codex/skills/` | `~/.codex/skills/` | Codex skill files |
| `gemini/GEMINI.md` | `~/.gemini/GEMINI.md` | Gemini global rules |
| `gemini/skills/` | `~/.gemini/skills/` | Gemini skill files |

The install script **will not** overwrite `settings.json` — that file contains your hooks and preferences.

## Local Web UI (`configure`)

`configure` runs a self-contained Python HTTP server at `http://localhost:4827`. Glass/aurora dark UI with a 3-theme picker (True Aurora, Sky Cyan, Violet).

**Sections**: Dashboard · CLAUDE.md Wizard · MCP Setup · Plugins · Project Templates · New Project

**Self-update**: Dashboard tab shows pending commits and applies updates with one click (pulls, reinstalls binary, restarts service).

Service management: `systemd` on Linux/WSL2, `launchd` on macOS — installed automatically by `install.sh`.

## New Project (30 seconds)

```bash
cp -r ~/Templates/claude-code-starter ~/Projects/my-new-app
cd ~/Projects/my-new-app
# Edit CLAUDE.md — fill in Project Name and Tech Stack
git init && git add . && git commit -m "chore: init from template"
```

## Aurora Theme

The glass/aurora design system is documented as a portable data sheet in `docs/themes.md` — drop the CSS variables and JS switcher into any dark web UI.

## Philosophy

- **Commits are checkpoints** — commit after every logical change, not just at session end
- **HANDOFF.md bridges sessions** — 100 lines of structured context > 500k tokens of history
- **DECISIONS.md is permanent** — commit it; HANDOFF.md is ephemeral, never commit it
- **Fresh sessions beat long sessions** — context rot is real after 200–300k tokens
- **Minimal MCP** — max 3–4 servers per session; each costs 100–500 tokens/turn

## License

MIT — fork, customize, share.
