# configure.py Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-file Python 3 local web server (`configure.py`) that provides a browser UI for managing Claude Code configs on port 4827.

**Architecture:** One Python file — constants and path helpers, testable API functions, an HTTP router class, embedded HTML/CSS/JS as a string constant, and a `main()` entry point that starts the server and opens the browser. Tests live in `tests/test_configure.py` and test the API functions directly without starting the server.

**Tech Stack:** Python 3.8+ stdlib only (`http.server`, `json`, `pathlib`, `urllib`, `webbrowser`, `threading`, `unittest`, `tempfile`)

---

## File Map

| File | Role |
|------|------|
| `configure.py` | Server, API functions, embedded HTML, entry point |
| `tests/test_configure.py` | Unit tests for all API functions |

---

## Task 1: Scaffold + Constants

**Files:**
- Create: `configure.py`
- Create: `tests/__init__.py`
- Create: `tests/test_configure.py`

- [ ] **Step 1.1: Write the failing import test**

```python
# tests/test_configure.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import unittest

class TestConstants(unittest.TestCase):
    def test_import(self):
        import configure
        self.assertEqual(configure.PORT, 4827)
        self.assertTrue(configure.CLAUDE_DIR.name == ".claude")
        self.assertTrue(configure.TEMPLATES_DIR.name == "Templates")
        self.assertTrue(configure.STARTER_DIR.name == "claude-code-starter")

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 1.2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_configure.py::TestConstants::test_import -v
```
Expected: `ModuleNotFoundError: No module named 'configure'`

- [ ] **Step 1.3: Create configure.py scaffold**

```python
# configure.py
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

# Maps logical names to filesystem paths
CONFIG_PATHS = {
    "CLAUDE.md":           CLAUDE_DIR / "CLAUDE.md",
    "mcp":                 CLAUDE_DIR / "claude_desktop_config.json",
    "settings":            CLAUDE_DIR / "settings.json",
    "template-claude":     STARTER_DIR / "CLAUDE.md",
    "template-decisions":  STARTER_DIR / "docs" / "DECISIONS.md",
}

KNOWN_PLUGINS = [
    {"id": "superpowers@claude-plugins-official",  "label": "Superpowers",     "description": "Core workflow skills (brainstorming, TDD, review)", "install": "/plugin install superpowers@claude-plugins-official"},
    {"id": "frontend-design@claude-plugins-official","label": "Frontend Design","description": "UI/UX component design",                           "install": "/plugin install frontend-design@claude-plugins-official"},
    {"id": "skill-creator@claude-plugins-official", "label": "Skill Creator",   "description": "Build custom skills",                              "install": "/plugin install skill-creator@claude-plugins-official"},
    {"id": "claude-mem@thedotmack",                 "label": "Claude Mem",      "description": "Cross-session memory",                             "install": "/plugin install claude-mem@thedotmack"},
    {"id": "caveman@caveman",                       "label": "Caveman",         "description": "Minimal alternative workflow",                      "install": "/plugin install caveman@caveman"},
]
```

- [ ] **Step 1.4: Create empty tests/__init__.py**

```bash
touch tests/__init__.py
```

- [ ] **Step 1.5: Run test to verify it passes**

```bash
python3 -m pytest tests/test_configure.py::TestConstants::test_import -v
```
Expected: `PASSED`

- [ ] **Step 1.6: Commit**

```bash
git add configure.py tests/__init__.py tests/test_configure.py
git commit -m "feat: scaffold configure.py with constants and path map"
```

---

## Task 2: get_status()

**Files:**
- Modify: `configure.py` — add `get_status()`
- Modify: `tests/test_configure.py` — add `TestGetStatus`

`get_status()` returns a dict `{"items": [...]}` where each item is `{"label": str, "status": "ok"|"warn"|"err", "message": str}`.

- [ ] **Step 2.1: Write the failing tests**

```python
# Add to tests/test_configure.py
import tempfile
from unittest.mock import patch

class TestGetStatus(unittest.TestCase):
    def test_returns_items_list(self):
        import configure
        result = configure.get_status()
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)

    def test_item_has_required_keys(self):
        import configure
        result = configure.get_status()
        for item in result["items"]:
            self.assertIn("label", item)
            self.assertIn("status", item)
            self.assertIn("message", item)
            self.assertIn(item["status"], ("ok", "warn", "err"))

    def test_missing_claude_dir_returns_err(self):
        import configure
        with patch.object(configure, "CLAUDE_DIR", Path("/nonexistent/path/.claude")):
            result = configure.get_status()
        claude_item = next(i for i in result["items"] if "CLAUDE.md" in i["label"])
        self.assertEqual(claude_item["status"], "err")

    def test_placeholder_token_returns_warn(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            mcp_path = Path(tmp) / "claude_desktop_config.json"
            mcp_path.write_text(json.dumps({"mcpServers": {"github": {"env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "REPLACE_WITH_YOUR_TOKEN"}}}}))
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "mcp": mcp_path}):
                result = configure.get_status()
        mcp_item = next(i for i in result["items"] if "MCP" in i["label"])
        self.assertEqual(mcp_item["status"], "warn")
```

- [ ] **Step 2.2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_configure.py::TestGetStatus -v
```
Expected: `AttributeError: module 'configure' has no attribute 'get_status'`

- [ ] **Step 2.3: Implement get_status()**

```python
# Add to configure.py after CONFIG_PATHS

def get_status() -> dict:
    items = []

    # CLAUDE.md
    p = CONFIG_PATHS["CLAUDE.md"]
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
        except (json.JSONDecodeError, Exception):
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


def _get_enabled_plugins() -> dict:
    """Read enabledPlugins from settings.json. Returns {} on any error."""
    settings_path = CONFIG_PATHS["settings"]
    if not settings_path.exists():
        return {}
    try:
        return json.loads(settings_path.read_text()).get("enabledPlugins", {})
    except Exception:
        return {}
```

- [ ] **Step 2.4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_configure.py::TestGetStatus -v
```
Expected: all 4 `PASSED`

- [ ] **Step 2.5: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: implement get_status() with health checks"
```

---

## Task 3: read_config() and write_config()

**Files:**
- Modify: `configure.py` — add `read_config()`, `write_config()`
- Modify: `tests/test_configure.py` — add `TestReadWriteConfig`

- [ ] **Step 3.1: Write the failing tests**

```python
# Add to tests/test_configure.py
class TestReadWriteConfig(unittest.TestCase):
    def test_read_existing_file(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "CLAUDE.md"
            p.write_text("# hello")
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "CLAUDE.md": p}):
                result = configure.read_config("CLAUDE.md")
        self.assertEqual(result["content"], "# hello")
        self.assertTrue(result["exists"])

    def test_read_missing_file(self):
        import configure
        with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "CLAUDE.md": Path("/no/such/file.md")}):
            result = configure.read_config("CLAUDE.md")
        self.assertFalse(result["exists"])
        self.assertEqual(result["content"], "")

    def test_read_unknown_name_returns_error(self):
        import configure
        result = configure.read_config("totally-unknown")
        self.assertFalse(result.get("exists", True))
        self.assertIn("error", result)

    def test_write_creates_file(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "CLAUDE.md"
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "CLAUDE.md": p}):
                result = configure.write_config("CLAUDE.md", "# new content")
        self.assertTrue(result["ok"])
        self.assertEqual(p.read_text(), "# new content")

    def test_write_creates_parent_dirs(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "sub" / "dir" / "file.md"
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "CLAUDE.md": p}):
                result = configure.write_config("CLAUDE.md", "content")
        self.assertTrue(result["ok"])
        self.assertTrue(p.exists())
```

- [ ] **Step 3.2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_configure.py::TestReadWriteConfig -v
```
Expected: `AttributeError: module 'configure' has no attribute 'read_config'`

- [ ] **Step 3.3: Implement read_config() and write_config()**

```python
# Add to configure.py

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
```

- [ ] **Step 3.4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_configure.py::TestReadWriteConfig -v
```
Expected: all 5 `PASSED`

- [ ] **Step 3.5: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: implement read_config() and write_config()"
```

---

## Task 4: get_plugins()

**Files:**
- Modify: `configure.py` — add `get_plugins()`
- Modify: `tests/test_configure.py` — add `TestGetPlugins`

`get_plugins()` returns `{"known": [...]}` where each entry merges `KNOWN_PLUGINS` with install state from `installed_plugins.json` and `settings.json`.

- [ ] **Step 4.1: Write the failing tests**

```python
# Add to tests/test_configure.py
class TestGetPlugins(unittest.TestCase):
    def _make_plugins_file(self, tmp, plugins_dict):
        p = Path(tmp) / "plugins" / "installed_plugins.json"
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({"version": 2, "plugins": plugins_dict}))
        return p

    def test_returns_known_list(self):
        import configure
        result = configure.get_plugins()
        self.assertIn("known", result)
        ids = [p["id"] for p in result["known"]]
        self.assertIn("superpowers@claude-plugins-official", ids)

    def test_installed_plugin_marked_correctly(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            self._make_plugins_file(tmp, {"superpowers@claude-plugins-official": [{"version": "5.1.0"}]})
            settings_path = Path(tmp) / "settings.json"
            settings_path.write_text(json.dumps({"enabledPlugins": {"superpowers@claude-plugins-official": True}}))
            with patch.object(configure, "CLAUDE_DIR", Path(tmp)):
                with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": settings_path}):
                    result = configure.get_plugins()
        sp = next(p for p in result["known"] if p["id"] == "superpowers@claude-plugins-official")
        self.assertTrue(sp["installed"])
        self.assertTrue(sp["enabled"])
        self.assertEqual(sp["version"], "5.1.0")

    def test_missing_plugins_file_returns_not_installed(self):
        import configure
        with patch.object(configure, "CLAUDE_DIR", Path("/nonexistent")):
            result = configure.get_plugins()
        for p in result["known"]:
            self.assertFalse(p["installed"])
```

- [ ] **Step 4.2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_configure.py::TestGetPlugins -v
```
Expected: `AttributeError: module 'configure' has no attribute 'get_plugins'`

- [ ] **Step 4.3: Implement get_plugins()**

```python
# Add to configure.py

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
```

- [ ] **Step 4.4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_configure.py::TestGetPlugins -v
```
Expected: all 3 `PASSED`

- [ ] **Step 4.5: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: implement get_plugins()"
```

---

## Task 5: update_enabled_plugins() and MCP helpers

**Files:**
- Modify: `configure.py` — add `update_enabled_plugins()`, `get_mcp_config()`, `write_mcp_config()`
- Modify: `tests/test_configure.py` — add `TestUpdatePlugins`, `TestMcpConfig`

- [ ] **Step 5.1: Write the failing tests**

```python
# Add to tests/test_configure.py
class TestUpdatePlugins(unittest.TestCase):
    def test_toggle_does_not_touch_other_keys(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            settings_path = Path(tmp) / "settings.json"
            settings_path.write_text(json.dumps({
                "hooks": {"SessionStart": []},
                "theme": "dark",
                "enabledPlugins": {"superpowers@claude-plugins-official": True}
            }))
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": settings_path}):
                configure.update_enabled_plugins({"claude-mem@thedotmack": True})
                result = json.loads(settings_path.read_text())
        self.assertIn("hooks", result)
        self.assertEqual(result["theme"], "dark")
        self.assertTrue(result["enabledPlugins"]["superpowers@claude-plugins-official"])
        self.assertTrue(result["enabledPlugins"]["claude-mem@thedotmack"])

    def test_toggle_creates_settings_if_missing(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            settings_path = Path(tmp) / "settings.json"
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": settings_path}):
                result = configure.update_enabled_plugins({"superpowers@claude-plugins-official": False})
        self.assertTrue(result["ok"])
        self.assertTrue(settings_path.exists())


class TestMcpConfig(unittest.TestCase):
    def test_get_mcp_returns_servers(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "mcp.json"
            p.write_text(json.dumps({"mcpServers": {"github": {"command": "npx"}}}))
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "mcp": p}):
                result = configure.get_mcp_config()
        self.assertIn("github", result.get("servers", {}))

    def test_write_mcp_saves_file(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "mcp.json"
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "mcp": p}):
                result = configure.write_mcp_config({"mcpServers": {"context7": {"command": "npx"}}})
        self.assertTrue(result["ok"])
        saved = json.loads(p.read_text())
        self.assertIn("context7", saved["mcpServers"])
```

- [ ] **Step 5.2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_configure.py::TestUpdatePlugins tests/test_configure.py::TestMcpConfig -v
```
Expected: `AttributeError`

- [ ] **Step 5.3: Implement update_enabled_plugins(), get_mcp_config(), write_mcp_config()**

```python
# Add to configure.py

def update_enabled_plugins(updates: dict) -> dict:
    """Merge updates into the enabledPlugins key only. All other settings.json keys untouched."""
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
    """Write full mcpServers config to claude_desktop_config.json."""
    mcp_path = CONFIG_PATHS["mcp"]
    try:
        mcp_path.parent.mkdir(parents=True, exist_ok=True)
        mcp_path.write_text(json.dumps(config, indent=2))
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

- [ ] **Step 5.4: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_configure.py::TestUpdatePlugins tests/test_configure.py::TestMcpConfig -v
```
Expected: all 4 `PASSED`

- [ ] **Step 5.5: Run full test suite**

```bash
python3 -m pytest tests/ -v
```
Expected: all tests `PASSED`

- [ ] **Step 5.6: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: implement update_enabled_plugins(), get_mcp_config(), write_mcp_config()"
```

---

## Task 6: HTTP Router

**Files:**
- Modify: `configure.py` — add `ConfigHandler` class and `HTML` constant (stub)

No unit tests for the HTTP layer — it's integration-level. We'll smoke-test it in Task 9.

- [ ] **Step 6.1: Add HTML stub and ConfigHandler**

```python
# Add to configure.py — place HTML constant before ConfigHandler

HTML = "<html><body><h1>oculus-configs</h1><p>UI loading...</p></body></html>"


class ConfigHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress request logs

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

        if path == "/" or path == "":
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
            name = path[len("/api/config/"):]
            self._send_json(read_config(name))

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path.startswith("/api/config/"):
            name = path[len("/api/config/"):]
            body = self._read_body()
            self._send_json(write_config(name, body.get("content", "")))

        elif path == "/api/mcp":
            body = self._read_body()
            self._send_json(write_mcp_config(body))

        elif path == "/api/plugins/toggle":
            body = self._read_body()
            plugin_id = body.get("id", "")
            enabled = body.get("enabled", False)
            self._send_json(update_enabled_plugins({plugin_id: enabled}))

        else:
            self._send_json({"error": "Not found"}, 404)
```

- [ ] **Step 6.2: Verify syntax is clean**

```bash
python3 -c "import configure; print('OK')"
```
Expected: `OK`

- [ ] **Step 6.3: Commit**

```bash
git add configure.py
git commit -m "feat: add HTTP router (ConfigHandler)"
```

---

## Task 7: Embed Full HTML UI

**Files:**
- Modify: `configure.py` — replace `HTML` stub with full embedded UI

- [ ] **Step 7.1: Replace the HTML stub with the full UI**

Replace the line `HTML = "<html><body>...</body></html>"` with:

```python
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>oculus-configs</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f0f0f;color:#e0e0e0;display:flex;height:100vh;overflow:hidden}
    nav{width:200px;background:#1a1a1a;padding:20px 0;flex-shrink:0;border-right:1px solid #2a2a2a;display:flex;flex-direction:column}
    nav h1{font-size:12px;color:#555;padding:0 20px 16px;text-transform:uppercase;letter-spacing:1px}
    nav a{display:block;padding:10px 20px;color:#888;text-decoration:none;font-size:14px;cursor:pointer;border-left:2px solid transparent}
    nav a:hover{color:#fff;background:#222}
    nav a.active{color:#fff;background:#222;border-left-color:#2563eb}
    main{flex:1;overflow-y:auto;padding:32px}
    section{display:none}
    section.active{display:block}
    h2{font-size:18px;font-weight:600;margin-bottom:20px;color:#fff}
    h3{font-size:14px;font-weight:600;margin-bottom:12px;color:#ccc}
    .status-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px;margin-bottom:24px}
    .card{background:#1a1a1a;border-radius:8px;padding:16px;border:1px solid #2a2a2a}
    .card .lbl{font-size:11px;color:#666;margin-bottom:6px;font-family:monospace}
    .card .val{font-size:13px;color:#e0e0e0;display:flex;align-items:center;gap:8px}
    .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
    .dot.ok{background:#22c55e}.dot.warn{background:#f59e0b}.dot.err{background:#ef4444}
    .form-group{margin-bottom:18px}
    label{display:block;font-size:12px;color:#888;margin-bottom:6px}
    input[type=text],textarea,select{width:100%;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:6px;color:#e0e0e0;padding:10px 12px;font-size:14px;font-family:inherit;outline:none}
    input[type=text]:focus,textarea:focus,select:focus{border-color:#2563eb}
    textarea{min-height:180px;resize:vertical;font-family:'Courier New',monospace;font-size:12px;line-height:1.5}
    select{background:#1a1a1a}
    btn,button{background:#2563eb;color:#fff;border:none;border-radius:6px;padding:10px 20px;font-size:14px;cursor:pointer;font-family:inherit}
    button:hover{background:#1d4ed8}
    button.sec{background:#252525}
    button.sec:hover{background:#333}
    .two-col{display:grid;grid-template-columns:1fr 1fr;gap:20px}
    table{width:100%;border-collapse:collapse;font-size:13px}
    th{text-align:left;color:#555;font-size:11px;text-transform:uppercase;padding:8px 12px;border-bottom:1px solid #222}
    td{padding:12px;border-bottom:1px solid #1e1e1e;color:#ccc}
    .toggle{position:relative;display:inline-block;width:38px;height:20px}
    .toggle input{opacity:0;width:0;height:0}
    .slider{position:absolute;cursor:pointer;inset:0;background:#333;border-radius:20px;transition:.2s}
    .slider:before{position:absolute;content:"";height:14px;width:14px;left:3px;bottom:3px;background:#fff;border-radius:50%;transition:.2s}
    input:checked+.slider{background:#2563eb}
    input:checked+.slider:before{transform:translateX(18px)}
    .code{font-family:'Courier New',monospace;background:#141414;border:1px solid #2a2a2a;border-radius:4px;padding:6px 10px;font-size:11px;color:#86efac;white-space:nowrap;overflow:auto;max-width:300px}
    .mcp-row{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;padding:14px 16px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;gap:16px}
    .mcp-row .inf{flex:1}
    .mcp-row .name{font-size:14px;color:#fff;margin-bottom:3px}
    .mcp-row .cost{font-size:11px;color:#666}
    .tabs{display:flex;gap:6px;margin-bottom:14px}
    .tab{padding:7px 14px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:6px;cursor:pointer;font-size:13px;color:#888}
    .tab.active{background:#2563eb;color:#fff;border-color:#2563eb}
    .hint{font-size:11px;color:#555;margin-top:5px}
    .toast{position:fixed;bottom:20px;right:20px;background:#22c55e;color:#fff;padding:10px 18px;border-radius:8px;font-size:13px;display:none;z-index:999}
    .toast.err{background:#ef4444}
    .cb-row{display:flex;align-items:flex-start;gap:8px;margin-bottom:10px}
    .cb-row input{margin-top:2px;flex-shrink:0}
    .cb-row .desc{font-size:12px;color:#666;margin-top:1px}
    pre#preview{background:#141414;border:1px solid #2a2a2a;border-radius:8px;padding:16px;font-size:11px;color:#86efac;overflow:auto;height:520px;white-space:pre-wrap;font-family:'Courier New',monospace;line-height:1.5}
  </style>
</head>
<body>
<nav>
  <h1>oculus-configs</h1>
  <a onclick="nav('dashboard',this)" class="active">Dashboard</a>
  <a onclick="nav('wizard',this)">CLAUDE.md</a>
  <a onclick="nav('mcp',this)">MCP Setup</a>
  <a onclick="nav('plugins',this)">Plugins</a>
  <a onclick="nav('templates',this)">Templates</a>
</nav>
<main>

<section id="dashboard" class="active">
  <h2>Config Status</h2>
  <div class="status-grid" id="status-grid"><div class="card"><div class="val">Loading...</div></div></div>
</section>

<section id="wizard">
  <h2>CLAUDE.md Wizard</h2>
  <div class="two-col">
    <div>
      <div class="form-group">
        <label>Active Plugins</label>
        <div id="plugin-checks"></div>
      </div>
      <div class="form-group">
        <label>Compact warning threshold</label>
        <select id="threshold">
          <option value="60">60% context used</option>
          <option value="70" selected>70% context used</option>
          <option value="80">80% context used</option>
        </select>
      </div>
      <div class="form-group">
        <label>Max MCP servers per session</label>
        <select id="maxmcp">
          <option value="2">2 servers</option>
          <option value="3">3 servers</option>
          <option value="4" selected>4 servers</option>
        </select>
      </div>
      <div class="form-group">
        <label>Custom notes (appended to file)</label>
        <textarea id="notes" placeholder="Project-specific rules, preferred languages, anything permanent..."></textarea>
      </div>
      <button onclick="saveClaudeMd()">Save to ~/.claude/CLAUDE.md</button>
    </div>
    <div>
      <label>Live Preview</label>
      <pre id="preview" style="margin-top:6px"></pre>
    </div>
  </div>
</section>

<section id="mcp">
  <h2>MCP Setup</h2>
  <div class="form-group" style="max-width:560px">
    <label>GitHub Personal Access Token</label>
    <input type="text" id="gh-token" placeholder="ghp_...">
    <p class="hint">Get one at github.com/settings/tokens &mdash; scopes: repo, read:org</p>
  </div>
  <h3>Servers</h3>
  <div id="mcp-list"></div>
  <button onclick="saveMcp()" style="margin-top:14px">Save MCP Config</button>
</section>

<section id="plugins">
  <h2>Plugins</h2>
  <table>
    <thead><tr><th>Plugin</th><th>Version</th><th>Installed</th><th>Enabled</th><th>Install Command</th></tr></thead>
    <tbody id="plugins-body"></tbody>
  </table>
</section>

<section id="templates">
  <h2>Project Templates</h2>
  <div class="tabs">
    <div class="tab active" onclick="switchTpl('template-claude',this)">CLAUDE.md</div>
    <div class="tab" onclick="switchTpl('template-decisions',this)">DECISIONS.md</div>
  </div>
  <textarea id="tpl-editor" style="min-height:480px"></textarea>
  <button onclick="saveTpl()" style="margin-top:12px">Save Template</button>
</section>

</main>
<div class="toast" id="toast"></div>

<script>
let plugData={};let mcpData={};let curTpl='template-claude';

function nav(id,el){
  document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('nav a').forEach(a=>a.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
  if(id==='dashboard')loadDash();
  if(id==='wizard')loadWizard();
  if(id==='mcp')loadMcp();
  if(id==='plugins')loadPlugins();
  if(id==='templates')loadTpl('template-claude');
}

function toast(msg,err=false){
  const t=document.getElementById('toast');
  t.textContent=msg;t.className='toast'+(err?' err':'');t.style.display='block';
  setTimeout(()=>t.style.display='none',3000);
}

async function api(path,method='GET',body=null){
  const opts={method,headers:{}};
  if(body){opts.headers['Content-Type']='application/json';opts.body=JSON.stringify(body);}
  const r=await fetch(path,opts);return r.json();
}

async function loadDash(){
  const d=await api('/api/status');
  document.getElementById('status-grid').innerHTML=d.items.map(i=>
    `<div class="card"><div class="lbl">${i.label}</div><div class="val"><span class="dot ${i.status}"></span>${i.message}</div></div>`
  ).join('');
}

async function loadWizard(){
  plugData=await api('/api/plugins');
  document.getElementById('plugin-checks').innerHTML=plugData.known.map(p=>
    `<div class="cb-row"><input type="checkbox" value="${p.id}" ${p.installed?'checked':''}><div><div>${p.label}</div><div class="desc">${p.description}</div></div></div>`
  ).join('');
  ['plugin-checks','notes','threshold','maxmcp'].forEach(id=>{
    document.getElementById(id).addEventListener('input',updatePreview);
    document.getElementById(id).addEventListener('change',updatePreview);
  });
  updatePreview();
}

function updatePreview(){
  const checked=[...document.querySelectorAll('#plugin-checks input:checked')].map(i=>i.value);
  const thr=document.getElementById('threshold').value;
  const mx=document.getElementById('maxmcp').value;
  const notes=document.getElementById('notes').value.trim();
  const plugLines=checked.map(id=>{
    const p=plugData.known.find(x=>x.id===id);
    return p?`### ${p.label} (${p.id}) — ENABLED\n- ${p.description}`:'';
  }).filter(Boolean).join('\n\n');
  document.getElementById('preview').textContent=
`# Global Claude Code Configuration
**Scope**: All projects on this machine

## Active Plugins

${plugLines||'(no plugins selected)'}

## Token Discipline (HIGH PRIORITY)

1. **One task per session** — don't reuse for unrelated work
2. **Check context at /usage** — compact or clear when approaching ${thr}%
3. **Use /compact selectively**: \`/compact focus on [active feature]\`
4. **Use subagents** for heavy or parallel work (10+ files)
5. **Keep MCP servers minimal** — max ${mx} per session; each costs 100–500 tokens/turn
6. **Fresh sessions beat long sessions** — context rot sets in after 200–300k tokens

## Workflow Standards

1. **Plan before execute** — Shift+Tab for plan mode
2. **Commit frequently** — every logical change is a checkpoint
3. **HANDOFF.md bridges sessions** — structured context beats history
4. **DECISIONS.md tracks architecture** — commit it; never commit HANDOFF.md

## Session End Checklist

- [ ] All work committed with descriptive message
- [ ] \`.claude/HANDOFF.md\` updated with next steps
- [ ] Push to remote if checkpoint is meaningful
${notes?'\n## Notes\n\n'+notes:''}
@~/.claude/rules/code-quality.md
@~/.claude/rules/plugin-usage.md`;
}

async function saveClaudeMd(){
  const content=document.getElementById('preview').textContent;
  const d=await api('/api/config/CLAUDE.md','POST',{content});
  d.ok?toast('Saved ~/.claude/CLAUDE.md'):toast('Error: '+d.error,true);
}

async function loadMcp(){
  mcpData=await api('/api/mcp');
  const token=mcpData.servers?.github?.env?.GITHUB_PERSONAL_ACCESS_TOKEN||'';
  document.getElementById('gh-token').value=token==='REPLACE_WITH_YOUR_TOKEN'?'':token;
  const servers=[
    {id:'github',name:'GitHub',desc:'PR and issue workflow',cost:'200–400 tokens/turn'},
    {id:'context7',name:'Context7',desc:'Live docs for fast-moving frameworks',cost:'100–300 tokens/turn'}
  ];
  document.getElementById('mcp-list').innerHTML=servers.map(s=>
    `<div class="mcp-row"><div class="inf"><div class="name">${s.name} &mdash; ${s.desc}</div><div class="cost">${s.cost}</div></div>
    <label class="toggle"><input type="checkbox" id="mcp-${s.id}" ${mcpData.servers?.[s.id]?'checked':''}><span class="slider"></span></label></div>`
  ).join('');
}

async function saveMcp(){
  const token=document.getElementById('gh-token').value.trim();
  const cfg={mcpServers:{}};
  if(document.getElementById('mcp-github').checked)
    cfg.mcpServers.github={command:'npx',args:['-y','@modelcontextprotocol/server-github'],env:{GITHUB_PERSONAL_ACCESS_TOKEN:token||'REPLACE_WITH_YOUR_TOKEN'}};
  if(document.getElementById('mcp-context7').checked)
    cfg.mcpServers.context7={command:'npx',args:['-y','@upstash/context7-mcp']};
  const d=await api('/api/mcp','POST',cfg);
  d.ok?toast('Saved MCP config'):toast('Error: '+d.error,true);
}

async function loadPlugins(){
  const data=await api('/api/plugins');
  document.getElementById('plugins-body').innerHTML=data.known.map(p=>
    `<tr>
      <td style="color:#fff">${p.label}</td>
      <td style="color:#555">${p.version||'—'}</td>
      <td><span class="dot ${p.installed?'ok':'err'}" style="display:inline-block;margin-right:6px"></span>${p.installed?'Yes':'No'}</td>
      <td>${p.installed?`<label class="toggle"><input type="checkbox" ${p.enabled?'checked':''} onchange="togglePlugin('${p.id}',this.checked)"><span class="slider"></span></label>`:'—'}</td>
      <td>${!p.installed?`<span class="code">${p.install}</span>`:'—'}</td>
    </tr>`
  ).join('');
}

async function togglePlugin(id,enabled){
  const d=await api('/api/plugins/toggle','POST',{id,enabled});
  d.ok?toast((enabled?'Enabled':'Disabled')+' '+id):toast('Error: '+d.error,true);
}

async function loadTpl(name){
  curTpl=name;
  const d=await api('/api/config/'+name);
  document.getElementById('tpl-editor').value=d.content||'';
}

function switchTpl(name,el){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');loadTpl(name);
}

async function saveTpl(){
  const content=document.getElementById('tpl-editor').value;
  const d=await api('/api/config/'+curTpl,'POST',{content});
  d.ok?toast('Template saved'):toast('Error: '+d.error,true);
}

loadDash();
</script>
</body>
</html>"""
```

- [ ] **Step 7.2: Verify syntax**

```bash
python3 -c "import configure; print('HTML length:', len(configure.HTML))"
```
Expected: `HTML length: <some number > 5000>`

- [ ] **Step 7.3: Commit**

```bash
git add configure.py
git commit -m "feat: embed full HTML/CSS/JS UI in configure.py"
```

---

## Task 8: main() — Server Startup and Browser Open

**Files:**
- Modify: `configure.py` — add `main()` at the bottom

- [ ] **Step 8.1: Add main()**

```python
# Add to the bottom of configure.py

def main():
    server = HTTPServer(("localhost", PORT), ConfigHandler)
    # Open browser half a second after server starts
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
```

- [ ] **Step 8.2: Verify the file runs without crashing (start + immediate kill)**

```bash
python3 configure.py &
sleep 1
curl -s http://localhost:4827/ | grep -o "oculus-configs"
kill %1
```
Expected output includes: `oculus-configs`

- [ ] **Step 8.3: Run full test suite one final time**

```bash
python3 -m pytest tests/ -v
```
Expected: all tests `PASSED`

- [ ] **Step 8.4: Final commit**

```bash
git add configure.py
git commit -m "feat: add main() entry point — configure.py is complete"
```

- [ ] **Step 8.5: Push**

```bash
git push origin main
```

---

## Self-Review Checklist

**Spec coverage:**
- [x] Single Python file, no pip deps — all stdlib imports
- [x] Port 4827
- [x] Auto-opens browser (threading.Timer + webbrowser)
- [x] GET /api/status — `get_status()`
- [x] GET /api/config/{file} — `read_config()`
- [x] POST /api/config/{file} — `write_config()`
- [x] GET /api/plugins — `get_plugins()`
- [x] POST /api/plugins/toggle — `update_enabled_plugins()`
- [x] GET /api/mcp + POST /api/mcp — `get_mcp_config()`, `write_mcp_config()`
- [x] Dashboard — status grid from `/api/status`
- [x] CLAUDE.md Wizard — form + live preview + save
- [x] MCP Setup — token input + server toggles
- [x] Plugins — table + enable/disable (enabledPlugins key only)
- [x] Templates — editor for template-claude and template-decisions

**Placeholder scan:** None found.

**Type consistency:** All function names used in the HTTP router match the implementations defined in Tasks 2–5.
