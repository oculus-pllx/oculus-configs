# Design: Gemini CLI Support + Template Completions

**Date**: 2026-05-14  
**Status**: Approved

---

## Scope

Three deliverables:

1. Add `mcp.json` to `templates/claude-code-starter/`
2. Add Gemini CLI support (`gemini/` directory + install.sh section 9)
3. Note that `apply_update` systemd restart is already fixed (no code change needed)

---

## 1. Template Completion — `mcp.json`

### What

Add `templates/claude-code-starter/mcp.json` alongside the existing `.gitignore` and `CLAUDE.md`.

### Content

Same structure as `claude/mcp.json` — `github` (with placeholder token) and `context7` servers. This gives new projects a ready-to-go MCP config that only needs a token filled in.

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "REPLACE_WITH_YOUR_TOKEN"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

### Deploy path

The `deploy_template` function in `configure.py` already handles `CLAUDE.md` and `DECISIONS.md`. `mcp.json` is a static file in the template directory — the install step (section 4) copies the whole `templates/claude-code-starter/` directory as-is, so it gets picked up automatically. No configure.py changes needed.

---

## 2. Gemini CLI Support

### Architecture

Mirrors the `codex/` directory structure exactly:

```
gemini/
├── GEMINI.md           ← global config (installed to ~/.gemini/GEMINI.md)
└── skills/
    ├── brainstorming/SKILL.md
    ├── finishing-a-development-branch/SKILL.md
    ├── receiving-code-review/SKILL.md
    ├── requesting-code-review/SKILL.md
    ├── systematic-debugging/SKILL.md
    ├── test-driven-development/SKILL.md
    ├── verification-before-completion/SKILL.md
    └── writing-plans/SKILL.md
```

### GEMINI.md

Content mirrors `codex/AGENTS.md` with two substitutions:

1. **Tool mapping table** — Gemini CLI equivalents instead of Codex equivalents (sourced from `gemini-tools.md`):

| Skill references | Gemini CLI equivalent |
|---|---|
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Edit` | `replace` |
| `Bash` | `run_shell_command` |
| `TodoWrite` | `write_todos` |
| `Skill` tool | `activate_skill` |
| `Task` subagent | `@generalist` with filled prompt |
| `WebSearch` | `google_web_search` |
| `WebFetch` | `web_fetch` |

2. **Skill trigger paths** — `read_file ~/.gemini/skills/<name>/SKILL.md` instead of `cat ~/.codex/skills/<name>/SKILL.md`. This is the lazy-load approach: skills are only read into context when their trigger fires, keeping session overhead low.

### Skills

The 8 skill files are direct copies of the codex equivalents (same workflow content, same tool names — the tool mapping in GEMINI.md handles translation). Starting as copies lets them diverge independently if Gemini-specific adaptations are needed later.

### install.sh section 9

Added after the Codex section:

```bash
# ── 9. Gemini CLI setup ─────────────────────────────────────────────────────
if command -v gemini &>/dev/null; then
  GEMINI_DIR="$HOME/.gemini"
  mkdir -p "$GEMINI_DIR/skills"

  if [ -f "$GEMINI_DIR/GEMINI.md" ]; then
    cp "$GEMINI_DIR/GEMINI.md" "$GEMINI_DIR/GEMINI.md.bak"
    echo "[info] ~/.gemini/GEMINI.md backed up to GEMINI.md.bak"
  fi
  cp "$REPO_DIR/gemini/GEMINI.md" "$GEMINI_DIR/GEMINI.md"
  echo "[ok]   ~/.gemini/GEMINI.md"

  cp -r "$REPO_DIR/gemini/skills/"* "$GEMINI_DIR/skills/"
  SKILL_COUNT=$(ls "$REPO_DIR/gemini/skills/" | wc -l | tr -d ' ')
  echo "[ok]   ~/.gemini/skills/ ($SKILL_COUNT skills installed)"
else
  echo "[skip] gemini not found — skipping Gemini CLI setup"
  echo "       Install Gemini CLI then re-run install.sh"
fi
```

### Tests

Add tests to `tests/test_configure.py` mirroring the existing Codex section tests:
- `test_gemini_skills_exist` — each of the 8 skills has a SKILL.md
- `test_gemini_md_exists` — `gemini/GEMINI.md` exists
- `test_gemini_md_has_tool_mapping` — GEMINI.md contains the tool mapping table
- `test_gemini_md_has_skill_triggers` — each of the 8 skill names appears in GEMINI.md

---

## 3. apply_update Restart — Already Fixed

`_restart_service()` was committed in `ce32402` and `apply_update()` already calls it (line 498 of `configure.py`). The HANDOFF.md gap note is stale. No code change needed — just update HANDOFF.md.

---

## Out of Scope

- Gemini CLI MCP config (Gemini doesn't use the same MCP format as Claude Code)
- Syncing skill content between codex/ and gemini/ — manual for now
- configure.py UI changes for Gemini
