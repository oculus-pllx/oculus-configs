# oculus-configs

Global AI CLI configurations for Claude Code (and eventually Codex, Gemini CLI).
Drop-in setup for a fresh workstation — one install script, ready to go.

## Structure

```
oculus-configs/
├── install.sh                    # One-shot install script
├── claude/                       # Claude Code configs → ~/.claude/
│   ├── CLAUDE.md                 # Global rules (all projects)
│   ├── mcp.json                  # MCP server config template
│   └── rules/
│       ├── code-quality.md       # Test thresholds, pre-commit checks
│       └── plugin-usage.md       # When to invoke which skill/plugin
├── templates/
│   └── claude-code-starter/      # Project template → ~/Templates/
│       ├── CLAUDE.md             # Project-specific config
│       ├── .gitignore
│       └── docs/
│           └── DECISIONS.md      # Architecture decision log
├── docs/                         # Reference guides and knowledge base
│   ├── setup-guide.md            # Complete workstation setup (30 min)
│   ├── quick-reference.md        # Cheat sheet (print this)
│   ├── visual-workflows.md       # Flowcharts and decision trees
│   └── project-templates.md      # Template files explained
├── codex/                        # (planned) Codex CLI configs
└── gemini/                       # (planned) Gemini CLI configs
```

## Quick Start

```bash
git clone git@github.com:oculus-pllx/oculus-configs.git
cd oculus-configs
./install.sh
```

Then in a Claude Code session:
```
/plugin install superpowers@claude-plugins-official
/plugin install frontend-design@claude-plugins-official
/plugin install skill-creator@claude-plugins-official
```

## What Gets Installed

| File | Destination | Purpose |
|------|-------------|---------|
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | Global rules for all sessions |
| `claude/rules/*.md` | `~/.claude/rules/` | Modular rule files |
| `claude/mcp.json` | `~/.claude/claude_desktop_config.json` | MCP server config (template) |
| `templates/claude-code-starter/` | `~/Templates/claude-code-starter/` | Project starter |

The install script **will not** overwrite `settings.json` — that file contains your hooks and preferences.

## New Project (30 seconds)

```bash
cp -r ~/Templates/claude-code-starter ~/Projects/my-new-app
cd ~/Projects/my-new-app
# Edit CLAUDE.md — fill in Project Name and Tech Stack
git init && git add . && git commit -m "chore: init from template"
```

## Fresh Workstation Setup

See `docs/setup-guide.md` for the complete walkthrough — install, plugins, MCP, first session.

## Philosophy

- **Commits are checkpoints** — commit after every logical change, not just at session end
- **HANDOFF.md bridges sessions** — 100 lines of structured context > 500k tokens of history
- **DECISIONS.md is permanent** — commit it; HANDOFF.md is ephemeral, never commit it
- **Fresh sessions beat long sessions** — context rot is real after 200–300k tokens
- **Minimal MCP** — max 3–4 servers per session; each costs 100–500 tokens/turn

## Planned Additions

- `codex/` — Codex CLI global config and project template
- `gemini/` — Gemini CLI (GEMINI.md) global config
- Shared `templates/` that work across all three CLIs

## License

MIT — fork, customize, share.
