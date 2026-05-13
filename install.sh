#!/usr/bin/env bash
# oculus-configs install script
# Drops Claude Code global configs into ~/.claude/
# Safe: will NOT overwrite settings.json (preserves hooks, etc.)

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
TEMPLATES_DIR="$HOME/Templates"

echo "=== oculus-configs install ==="
echo "Repo:      $REPO_DIR"
echo "Claude:    $CLAUDE_DIR"
echo "Templates: $TEMPLATES_DIR"
echo ""

# ── 1. Global CLAUDE.md ──────────────────────────────────────────────────────
if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
  echo "[skip] ~/.claude/CLAUDE.md already exists (backup at CLAUDE.md.bak)"
  cp "$CLAUDE_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md.bak"
fi
cp "$REPO_DIR/claude/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
echo "[ok]   ~/.claude/CLAUDE.md"

# ── 2. Rules directory ────────────────────────────────────────────────────────
mkdir -p "$CLAUDE_DIR/rules"
cp "$REPO_DIR/claude/rules/"*.md "$CLAUDE_DIR/rules/"
echo "[ok]   ~/.claude/rules/"

# ── 3. MCP config template ───────────────────────────────────────────────────
MCP_TARGET="$CLAUDE_DIR/claude_desktop_config.json"
if [ -f "$MCP_TARGET" ]; then
  echo "[skip] ~/.claude/claude_desktop_config.json exists — not overwriting"
  echo "       Template at: $REPO_DIR/claude/mcp.json"
else
  cp "$REPO_DIR/claude/mcp.json" "$MCP_TARGET"
  echo "[ok]   ~/.claude/claude_desktop_config.json (add your GitHub token!)"
fi

# ── 4. Project starter template ───────────────────────────────────────────────
mkdir -p "$TEMPLATES_DIR"
if [ -d "$TEMPLATES_DIR/claude-code-starter" ]; then
  echo "[skip] ~/Templates/claude-code-starter already exists"
else
  cp -r "$REPO_DIR/templates/claude-code-starter" "$TEMPLATES_DIR/"
  echo "[ok]   ~/Templates/claude-code-starter"
fi

echo ""
echo "=== Done ==="
echo ""
echo "Next steps:"
echo "  1. Edit ~/.claude/CLAUDE.md — review and customize"
echo "  2. Add GitHub token to ~/.claude/claude_desktop_config.json"
echo "     Get one at: https://github.com/settings/tokens"
echo "  3. Install plugins inside a Claude Code session:"
echo "     /plugin install superpowers@claude-plugins-official"
echo "     /plugin install frontend-design@claude-plugins-official"
echo "     /plugin install skill-creator@claude-plugins-official"
echo "  4. New project: cp -r ~/Templates/claude-code-starter ~/Projects/my-app"
echo ""
