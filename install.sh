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

# ── 5. Install configure binary ───────────────────────────────────────────────
mkdir -p "$HOME/.local/bin"
cp "$REPO_DIR/configure.py" "$HOME/.local/bin/configure"
chmod +x "$HOME/.local/bin/configure"
echo "[ok]   ~/.local/bin/configure"
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
  echo "[warn] ~/.local/bin is not in your PATH"
  echo "       Add to ~/.bashrc or ~/.zshrc:"
  echo "         export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

# ── 6. Record repo path in settings.json ──────────────────────────────────────
python3 - "$REPO_DIR" "$HOME/.claude/settings.json" <<'PYEOF'
import json, pathlib, sys
repo_dir, settings_path = sys.argv[1], sys.argv[2]
p = pathlib.Path(settings_path)
d = json.loads(p.read_text()) if p.exists() else {}
d.setdefault("oculus", {})["repo_path"] = repo_dir
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(d, indent=2))
PYEOF
echo "[ok]   ~/.claude/settings.json (repo_path recorded)"

# ── 7. Service setup ──────────────────────────────────────────────────────────
OS=$(uname -s)
UNAME_R=$(uname -r | tr '[:upper:]' '[:lower:]')
CONFIGURE_BIN="$HOME/.local/bin/configure"

if [[ "$OS" == "Linux" ]]; then
  SERVICE_DIR="$HOME/.config/systemd/user"
  SERVICE_FILE="$SERVICE_DIR/oculus-configure.service"
  mkdir -p "$SERVICE_DIR"
  systemctl --user stop oculus-configure 2>/dev/null || true
  cat > "$SERVICE_FILE" <<UNIT
[Unit]
Description=oculus-configs UI
After=network.target

[Service]
ExecStart=$CONFIGURE_BIN
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
UNIT
  if systemctl --user daemon-reload 2>/dev/null && \
     systemctl --user enable oculus-configure 2>/dev/null && \
     systemctl --user start oculus-configure 2>/dev/null; then
    echo "[ok]   systemd user service: oculus-configure"
  else
    echo "[warn] systemd unavailable — run 'configure' manually to start the UI"
  fi
  if echo "$UNAME_R" | grep -q "microsoft"; then
    loginctl enable-linger "$USER" 2>/dev/null || true
    echo "[ok]   WSL2: loginctl linger enabled (service survives login)"
  fi

elif [[ "$OS" == "Darwin" ]]; then
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PLIST_FILE="$PLIST_DIR/com.oculus.configure.plist"
  mkdir -p "$PLIST_DIR"
  launchctl unload "$PLIST_FILE" 2>/dev/null || true
  cat > "$PLIST_FILE" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.oculus.configure</string>
  <key>ProgramArguments</key>
  <array><string>$CONFIGURE_BIN</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/oculus-configure.log</string>
  <key>StandardErrorPath</key><string>/tmp/oculus-configure.log</string>
</dict>
</plist>
PLIST
  launchctl load "$PLIST_FILE"
  echo "[ok]   launchd agent: com.oculus.configure"

else
  echo "[warn] Unknown platform — service not installed"
  echo "       Run manually: configure"
fi

# ── 8. Codex CLI setup ──────────────────────────────────────────────────────
if command -v codex &>/dev/null; then
  CODEX_DIR="$HOME/.codex"
  mkdir -p "$CODEX_DIR/skills"

  if [ -f "$CODEX_DIR/AGENTS.md" ]; then
    cp "$CODEX_DIR/AGENTS.md" "$CODEX_DIR/AGENTS.md.bak"
    echo "[info] ~/.codex/AGENTS.md backed up to AGENTS.md.bak"
  fi
  cp "$REPO_DIR/codex/AGENTS.md" "$CODEX_DIR/AGENTS.md"
  echo "[ok]   ~/.codex/AGENTS.md"

  cp -r "$REPO_DIR/codex/skills/"* "$CODEX_DIR/skills/"
  SKILL_COUNT=$(ls "$REPO_DIR/codex/skills/" | wc -l | tr -d ' ')
  echo "[ok]   ~/.codex/skills/ ($SKILL_COUNT skills installed)"
else
  echo "[skip] codex not found — skipping Codex CLI setup"
  echo "       Install Codex then re-run install.sh"
fi

# ── 9. Gemini CLI setup ──────────────────────────────────────────────────────
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

echo ""
echo "=== Done ==="
echo ""
echo "The configure UI is running at http://localhost:4827"
echo "It starts automatically on login."
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:4827 in your browser"
echo "  2. Add GitHub token via MCP Setup tab"
echo "  3. Install plugins inside a Claude Code session:"
echo "     /plugin install superpowers@claude-plugins-official"
echo ""
