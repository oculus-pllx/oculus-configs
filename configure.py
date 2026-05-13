from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json
import os
import webbrowser
import threading
import urllib.parse

PORT = 4827
CLAUDE_DIR = Path.home() / ".claude"
TEMPLATES_DIR = Path.home() / "Templates"
STARTER_DIR = TEMPLATES_DIR / "claude-code-starter"

CONFIG_PATHS = {
    "CLAUDE.md":          CLAUDE_DIR / "CLAUDE.md",
    "mcp":                CLAUDE_DIR / "claude_desktop_config.json",
    "settings":           CLAUDE_DIR / "settings.json",
    "template-claude":    STARTER_DIR / "CLAUDE.md",
    "template-decisions": STARTER_DIR / "docs" / "DECISIONS.md",
}

KNOWN_PLUGINS = [
    {"id": "superpowers@claude-plugins-official",   "label": "Superpowers",      "description": "Core workflow skills (brainstorming, TDD, review)", "install": "/plugin install superpowers@claude-plugins-official"},
    {"id": "frontend-design@claude-plugins-official","label": "Frontend Design",  "description": "UI/UX component design",                           "install": "/plugin install frontend-design@claude-plugins-official"},
    {"id": "skill-creator@claude-plugins-official",  "label": "Skill Creator",    "description": "Build custom skills",                              "install": "/plugin install skill-creator@claude-plugins-official"},
    {"id": "claude-mem@thedotmack",                  "label": "Claude Mem",       "description": "Cross-session memory",                             "install": "/plugin install claude-mem@thedotmack"},
    {"id": "caveman@caveman",                        "label": "Caveman",          "description": "Minimal alternative workflow",                      "install": "/plugin install caveman@caveman"},
]


# ── API functions ─────────────────────────────────────────────────────────────

def _get_enabled_plugins() -> dict:
    settings_path = CONFIG_PATHS["settings"]
    if not settings_path.exists():
        return {}
    try:
        return json.loads(settings_path.read_text()).get("enabledPlugins", {})
    except Exception:
        return {}


def get_status() -> dict:
    items = []

    # CLAUDE.md
    p = CLAUDE_DIR / "CLAUDE.md"
    if p.exists():
        items.append({"label": "~/.claude/CLAUDE.md", "status": "ok", "message": "Installed"})
    else:
        items.append({"label": "~/.claude/CLAUDE.md", "status": "err", "message": "Missing — run install.sh"})

    # rules/
    rules_dir = CLAUDE_DIR / "rules"
    if rules_dir.exists() and any(rules_dir.iterdir()):
        items.append({"label": "~/.claude/rules/", "status": "ok", "message": f"{len(list(rules_dir.glob('*.md')))} rule files"})
    else:
        items.append({"label": "~/.claude/rules/", "status": "warn", "message": "Empty or missing"})

    # MCP config
    mcp_path = CONFIG_PATHS["mcp"]
    if not mcp_path.exists():
        items.append({"label": "MCP Config", "status": "err", "message": "Missing — run install.sh"})
    else:
        try:
            mcp = json.loads(mcp_path.read_text())
            token = mcp.get("mcpServers", {}).get("github", {}).get("env", {}).get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
            if token in ("", "REPLACE_WITH_YOUR_TOKEN"):
                items.append({"label": "MCP Config", "status": "warn", "message": "Present — GitHub token not set"})
            else:
                items.append({"label": "MCP Config", "status": "ok", "message": "Configured"})
        except Exception:
            items.append({"label": "MCP Config", "status": "err", "message": "Invalid JSON"})

    # Templates
    if STARTER_DIR.exists():
        items.append({"label": "~/Templates/claude-code-starter", "status": "ok", "message": "Installed"})
    else:
        items.append({"label": "~/Templates/claude-code-starter", "status": "err", "message": "Missing — run install.sh"})

    # Plugins
    plugins_path = CLAUDE_DIR / "plugins" / "installed_plugins.json"
    enabled_plugins = _get_enabled_plugins()
    if plugins_path.exists():
        try:
            data = json.loads(plugins_path.read_text())
            installed = list(data.get("plugins", {}).keys())
            enabled = [p for p in installed if enabled_plugins.get(p, False)]
            items.append({"label": "Plugins", "status": "ok", "message": f"{len(installed)} installed, {len(enabled)} enabled"})
        except Exception:
            items.append({"label": "Plugins", "status": "warn", "message": "Could not read plugin state"})
    else:
        items.append({"label": "Plugins", "status": "warn", "message": "No plugins installed"})

    return {"items": items}


def read_config(name: str) -> dict:
    if name not in CONFIG_PATHS:
        return {"exists": False, "content": "", "error": f"Unknown config name: {name}"}
    p = CONFIG_PATHS[name]
    if not p.exists():
        return {"exists": False, "content": ""}
    try:
        return {"exists": True, "content": p.read_text(encoding="utf-8")}
    except Exception as e:
        return {"exists": True, "content": "", "error": str(e)}


def write_config(name: str, content: str) -> dict:
    if name not in CONFIG_PATHS:
        return {"ok": False, "error": f"Unknown config name: {name}"}
    p = CONFIG_PATHS[name]
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_plugins() -> dict:
    plugins_path = CLAUDE_DIR / "plugins" / "installed_plugins.json"
    enabled = _get_enabled_plugins()
    installed_data = {}
    if plugins_path.exists():
        try:
            raw = json.loads(plugins_path.read_text())
            installed_data = raw.get("plugins", {})
        except Exception:
            pass
    known = []
    for p in KNOWN_PLUGINS:
        pid = p["id"]
        entry = {**p}
        if pid in installed_data:
            versions = installed_data[pid]
            entry["installed"] = True
            entry["version"] = versions[0].get("version", "unknown") if versions else "unknown"
        else:
            entry["installed"] = False
            entry["version"] = None
        entry["enabled"] = enabled.get(pid, False)
        known.append(entry)
    return {"known": known}


def update_enabled_plugins(updates: dict) -> dict:
    settings_path = CONFIG_PATHS["settings"]
    try:
        existing = json.loads(settings_path.read_text()) if settings_path.exists() else {}
        existing.setdefault("enabledPlugins", {}).update(updates)
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(existing, indent=2))
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_mcp_config() -> dict:
    mcp_path = CONFIG_PATHS["mcp"]
    if not mcp_path.exists():
        return {"servers": {}}
    try:
        data = json.loads(mcp_path.read_text())
        return {"servers": data.get("mcpServers", {})}
    except Exception as e:
        return {"servers": {}, "error": str(e)}


def write_mcp_config(config: dict) -> dict:
    mcp_path = CONFIG_PATHS["mcp"]
    try:
        mcp_path.parent.mkdir(parents=True, exist_ok=True)
        mcp_path.write_text(json.dumps(config, indent=2))
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── HTTP layer ────────────────────────────────────────────────────────────────

HTML = "<html><body><h1>oculus-configs</h1><p>UI loading...</p></body></html>"


class ConfigHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data: dict, status: int = 200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length)) if length else {}

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", ""):
            body = HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/api/status":
            self._send_json(get_status())
        elif path == "/api/plugins":
            self._send_json(get_plugins())
        elif path == "/api/mcp":
            self._send_json(get_mcp_config())
        elif path.startswith("/api/config/"):
            self._send_json(read_config(path[len("/api/config/"):]))
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path.startswith("/api/config/"):
            body = self._read_body()
            self._send_json(write_config(path[len("/api/config/"):], body.get("content", "")))
        elif path == "/api/mcp":
            self._send_json(write_mcp_config(self._read_body()))
        elif path == "/api/plugins/toggle":
            body = self._read_body()
            self._send_json(update_enabled_plugins({body.get("id", ""): body.get("enabled", False)}))
        else:
            self._send_json({"error": "Not found"}, 404)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    server = HTTPServer(("localhost", PORT), ConfigHandler)
    threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    print(f"oculus-configs UI → http://localhost:{PORT}")
    print("Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
