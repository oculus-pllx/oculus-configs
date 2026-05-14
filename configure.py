from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
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

TEMPLATE_FILES = {
    "CLAUDE.md":         STARTER_DIR / "CLAUDE.md",
    "docs/DECISIONS.md": STARTER_DIR / "docs" / "DECISIONS.md",
    ".gitignore":        STARTER_DIR / ".gitignore",
    "mcp.json":          STARTER_DIR / "mcp.json",
}


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
        items.append({"label": "~/.claude/CLAUDE.md", "status": "ok", "message": "Installed",
                      "desc": "Global instructions Claude reads at the start of every session"})
    else:
        items.append({"label": "~/.claude/CLAUDE.md", "status": "err", "message": "Missing",
                      "desc": "Global instructions Claude reads at the start of every session",
                      "fix": "Run bash install.sh in the oculus-configs folder"})

    # rules/
    rules_dir = CLAUDE_DIR / "rules"
    if rules_dir.exists() and any(rules_dir.iterdir()):
        items.append({"label": "~/.claude/rules/", "status": "ok",
                      "message": f"{len(list(rules_dir.glob('*.md')))} rule files",
                      "desc": "Modular rule files imported by CLAUDE.md (code quality, plugin usage)"})
    else:
        items.append({"label": "~/.claude/rules/", "status": "warn", "message": "Empty or missing",
                      "desc": "Modular rule files imported by CLAUDE.md",
                      "fix": "Run bash install.sh in the oculus-configs folder"})

    # MCP config
    mcp_path = CONFIG_PATHS["mcp"]
    if not mcp_path.exists():
        items.append({"label": "MCP Config", "status": "err", "message": "Missing",
                      "desc": "Connects Claude to external tools (GitHub, docs) during sessions",
                      "fix": "Run bash install.sh in the oculus-configs folder"})
    else:
        try:
            mcp = json.loads(mcp_path.read_text())
            token = mcp.get("mcpServers", {}).get("github", {}).get("env", {}).get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
            if token in ("", "REPLACE_WITH_YOUR_TOKEN"):
                items.append({"label": "MCP Config", "status": "warn", "message": "GitHub token not set",
                              "desc": "Connects Claude to external tools (GitHub, docs) during sessions",
                              "fix": "Go to MCP Setup tab → paste your GitHub token → Save"})
            else:
                items.append({"label": "MCP Config", "status": "ok", "message": "Configured",
                              "desc": "Connects Claude to external tools (GitHub, docs) during sessions"})
        except Exception:
            items.append({"label": "MCP Config", "status": "err", "message": "Invalid JSON",
                          "desc": "Connects Claude to external tools (GitHub, docs) during sessions",
                          "fix": "Go to MCP Setup tab and re-save the config"})

    # Templates
    if STARTER_DIR.exists():
        items.append({"label": "~/Templates/claude-code-starter", "status": "ok", "message": "Installed",
                      "desc": "Starter CLAUDE.md and DECISIONS.md copied into new projects"})
    else:
        items.append({"label": "~/Templates/claude-code-starter", "status": "err", "message": "Missing",
                      "desc": "Starter CLAUDE.md and DECISIONS.md copied into new projects",
                      "fix": "Run bash install.sh in the oculus-configs folder"})

    # Plugins
    plugins_path = CLAUDE_DIR / "plugins" / "installed_plugins.json"
    enabled_plugins = _get_enabled_plugins()
    if plugins_path.exists():
        try:
            data = json.loads(plugins_path.read_text())
            installed = list(data.get("plugins", {}).keys())
            enabled = [p for p in installed if enabled_plugins.get(p, False)]
            items.append({"label": "Plugins", "status": "ok",
                          "message": f"{len(installed)} installed, {len(enabled)} enabled",
                          "desc": "Skill packs that extend Claude's workflow capabilities"})
        except Exception:
            items.append({"label": "Plugins", "status": "warn", "message": "Could not read plugin state",
                          "desc": "Skill packs that extend Claude's workflow capabilities"})
    else:
        items.append({"label": "Plugins", "status": "warn", "message": "No plugins installed",
                      "desc": "Skill packs that extend Claude's workflow capabilities",
                      "fix": "Open Claude Code and run: /plugin install superpowers@claude-plugins-official"})

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


def get_branding() -> dict:
    settings_path = CONFIG_PATHS["settings"]
    try:
        data = json.loads(settings_path.read_text()) if settings_path.exists() else {}
        return data.get("oculus", {}).get("branding", {"name": "", "logo": ""})
    except Exception:
        return {"name": "", "logo": ""}


def write_branding(branding: dict) -> dict:
    settings_path = CONFIG_PATHS["settings"]
    try:
        existing = json.loads(settings_path.read_text()) if settings_path.exists() else {}
        existing.setdefault("oculus", {})["branding"] = branding
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(existing, indent=2))
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def write_mcp_config(config: dict) -> dict:
    mcp_path = CONFIG_PATHS["mcp"]
    try:
        mcp_path.parent.mkdir(parents=True, exist_ok=True)
        mcp_path.write_text(json.dumps(config, indent=2))
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def browse_dir(path: str) -> dict:
    try:
        p = Path(path).expanduser().resolve()
        if not p.exists() or not p.is_dir():
            return {"error": f"Not a directory: {path}"}
        dirs = sorted(
            [d.name for d in p.iterdir() if d.is_dir() and not d.name.startswith(".")],
            key=str.lower
        )
        parent = str(p.parent) if p.parent != p else None
        return {"path": str(p), "dirs": dirs, "parent": parent}
    except PermissionError:
        return {"error": "Permission denied", "path": path, "dirs": [], "parent": str(Path(path).parent)}
    except Exception as e:
        return {"error": str(e)}


def which_gh() -> dict:
    return {
        "gh": shutil.which("gh") is not None,
        "code": shutil.which("code") is not None,
    }


def slugify(name: str) -> str:
    return re.sub(r'[^a-z0-9-]', '-', name.lower())


def _copy_templates(dest: Path, templates: list):
    for name in templates:
        src = TEMPLATE_FILES.get(name)
        if src and src.exists():
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(src.read_bytes())


def create_project(name: str, parent: str, templates: list) -> dict:
    slug = slugify(name)
    path = Path(parent).expanduser() / slug
    if path.exists():
        return {"ok": False, "error": "Folder already exists"}
    try:
        path.mkdir(parents=True)
        _copy_templates(path, templates)
        for cmd in [
            ["git", "init", "-b", "main"],
            ["git", "add", "-A"],
            ["git", "commit", "-m", "Initial commit", "--allow-empty"],
        ]:
            r = subprocess.run(cmd, cwd=path, capture_output=True, text=True)
            if r.returncode != 0:
                return {"ok": False, "error": r.stderr.strip(), "path": str(path)}
        git_log = subprocess.run(
            ["git", "log", "--oneline"], cwd=path, capture_output=True, text=True
        ).stdout.strip()
        return {"ok": True, "path": str(path), "git_log": git_log}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def github_project(path: str, repo_name: str, private: bool) -> dict:
    if not shutil.which("gh"):
        return {"ok": False, "error": "gh CLI not found in PATH"}
    flag = "--private" if private else "--public"
    r = subprocess.run(
        ["gh", "repo", "create", repo_name, flag, "--source", path, "--push"],
        capture_output=True, text=True
    )
    if r.returncode != 0:
        return {"ok": False, "error": r.stderr.strip() or r.stdout.strip()}
    remote = subprocess.run(
        ["git", "remote", "get-url", "origin"], cwd=path, capture_output=True, text=True
    )
    return {"ok": True, "clone_url": remote.stdout.strip()}


def remote_project(path: str, remote_url: str) -> dict:
    for cmd in [
        ["git", "remote", "add", "origin", remote_url],
        ["git", "push", "-u", "origin", "main"],
    ]:
        r = subprocess.run(cmd, cwd=path, capture_output=True, text=True)
        if r.returncode != 0:
            return {"ok": False, "error": r.stderr.strip()}
    return {"ok": True, "clone_url": remote_url}


def open_vscode(path: str) -> dict:
    subprocess.Popen(["code", path])
    return {"ok": True}


TEMPLATE_DEST = {
    "template-claude":    "CLAUDE.md",
    "template-decisions": os.path.join("docs", "DECISIONS.md"),
}


def deploy_template(file: str, dest_dir: str, content: str) -> dict:
    if file not in TEMPLATE_DEST:
        return {"ok": False, "error": f"Unknown template: {file}"}
    dest_path = Path(dest_dir).expanduser() / TEMPLATE_DEST[file]
    try:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(content, encoding="utf-8")
        return {"ok": True, "path": str(dest_path)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── HTTP layer ────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>oculus-configs</title>
  <style>
    *{box-sizing:border-box;margin:0;padding:0}
    :root{--bg:#0f0f0f;--surface:#1a1a1a;--surface-deep:#141414;--surface-hover:#222;--border:#2a2a2a;--border-sub:#1e1e1e;--btn-sec:#252525;--btn-sec-hover:#333;--text:#e0e0e0;--text-2:#ccc;--text-3:#888;--text-4:#666;--text-5:#555;--text-6:#444;--text-strong:#fff;--accent:#2563eb;--accent-hover:#1d4ed8;--code-fg:#86efac;--ok:#22c55e;--warn:#f59e0b;--err:#ef4444;--warn-border:#78350f;--err-border:#7f1d1d;--slider-bg:#333;--overlay:rgba(0,0,0,0.75);--shadow:0 20px 60px rgba(0,0,0,0.5);--badge-gb:#1e3a5f;--badge-gf:#60a5fa;--badge-pb:#1a2e1a;--badge-pf:#4ade80}
    body.light{--bg:#f5f5f5;--surface:#fff;--surface-deep:#f0f0f0;--surface-hover:#ebebeb;--border:#e0e0e0;--border-sub:#ebebeb;--btn-sec:#e8e8e8;--btn-sec-hover:#d8d8d8;--text:#111;--text-2:#333;--text-3:#555;--text-4:#777;--text-5:#999;--text-6:#bbb;--text-strong:#111;--code-fg:#166534;--ok:#16a34a;--warn:#d97706;--err:#dc2626;--warn-border:#d97706;--err-border:#dc2626;--slider-bg:#ccc;--overlay:rgba(0,0,0,0.5);--shadow:0 20px 60px rgba(0,0,0,0.15);--badge-gb:#dbeafe;--badge-gf:#1d4ed8;--badge-pb:#dcfce7;--badge-pf:#166534}
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);display:flex;height:100vh;overflow:hidden;transition:background .2s,color .2s}
    nav{width:200px;background:var(--surface);padding:20px 0;flex-shrink:0;border-right:1px solid var(--border);display:flex;flex-direction:column}
    nav h1{font-size:12px;color:var(--text-5);padding:0 20px 16px;text-transform:uppercase;letter-spacing:1px}
    nav a{display:block;padding:10px 20px;color:var(--text-3);text-decoration:none;font-size:14px;cursor:pointer;border-left:2px solid transparent}
    nav a:hover{color:var(--text-strong);background:var(--surface-hover)}
    nav a.active{color:var(--text-strong);background:var(--surface-hover);border-left-color:var(--accent)}
    main{flex:1;overflow-y:auto;padding:32px}
    section{display:none}
    section.active{display:block}
    h2{font-size:18px;font-weight:600;margin-bottom:6px;color:var(--text-strong)}
    h3{font-size:14px;font-weight:600;margin-bottom:10px;color:var(--text-2);margin-top:20px}
    .section-desc{font-size:13px;color:var(--text-4);margin-bottom:20px;line-height:1.5;max-width:700px}
    .section-desc strong{color:var(--text-3)}
    .status-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px;margin-bottom:24px}
    .card{background:var(--surface);border-radius:8px;padding:16px;border:1px solid var(--border)}
    .card.warn{border-color:var(--warn-border)}.card.err{border-color:var(--err-border)}
    .card .lbl{font-size:11px;color:var(--text-4);margin-bottom:4px;font-family:monospace}
    .card .card-desc{font-size:11px;color:var(--text-6);margin-bottom:8px;line-height:1.4}
    .card .val{font-size:13px;color:var(--text);display:flex;align-items:center;gap:8px}
    .card .fix{font-size:11px;color:var(--warn);margin-top:8px;padding-top:8px;border-top:1px solid var(--border);line-height:1.4}
    .card .fix::before{content:"→ "}
    .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
    .dot.ok{background:var(--ok)}.dot.warn{background:var(--warn)}.dot.err{background:var(--err)}
    .form-group{margin-bottom:20px}
    .field-label{font-size:12px;color:var(--text-3);margin-bottom:4px;display:block}
    .field-help{font-size:11px;color:var(--text-5);margin-top:5px;line-height:1.5}
    label{display:block;font-size:12px;color:var(--text-3);margin-bottom:6px}
    input[type=text],textarea,select{width:100%;background:var(--surface);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:10px 12px;font-size:14px;font-family:inherit;outline:none}
    input[type=text]:focus,textarea:focus,select:focus{border-color:var(--accent)}
    textarea{min-height:180px;resize:vertical;font-family:'Courier New',monospace;font-size:12px;line-height:1.5}
    select{background:var(--surface)}
    button{background:var(--accent);color:#fff;border:none;border-radius:6px;padding:10px 20px;font-size:14px;cursor:pointer;font-family:inherit}
    button:hover{background:var(--accent-hover)}
    button.sec{background:var(--btn-sec);color:var(--text-2)}
    button.sec:hover{background:var(--btn-sec-hover)}
    .two-col{display:grid;grid-template-columns:1fr 1fr;gap:24px}
    table{width:100%;border-collapse:collapse;font-size:13px}
    th{text-align:left;color:var(--text-5);font-size:11px;text-transform:uppercase;padding:8px 12px;border-bottom:1px solid var(--border)}
    td{padding:12px;border-bottom:1px solid var(--border-sub);color:var(--text-2);vertical-align:top}
    .toggle{position:relative;display:inline-block;width:38px;height:20px}
    .toggle input{opacity:0;width:0;height:0}
    .slider{position:absolute;cursor:pointer;inset:0;background:var(--slider-bg);border-radius:20px;transition:.2s}
    .slider:before{position:absolute;content:"";height:14px;width:14px;left:3px;bottom:3px;background:#fff;border-radius:50%;transition:.2s}
    input:checked+.slider{background:var(--accent)}
    input:checked+.slider:before{transform:translateX(18px)}
    .code{font-family:'Courier New',monospace;background:var(--surface-deep);border:1px solid var(--border);border-radius:4px;padding:6px 10px;font-size:11px;color:var(--code-fg);white-space:nowrap;overflow-x:auto;max-width:300px;display:block}
    .mcp-row{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:flex-start;gap:16px}
    .mcp-row .inf{flex:1}
    .mcp-row .name{font-size:14px;color:var(--text-strong);margin-bottom:3px}
    .mcp-row .mcp-desc{font-size:12px;color:var(--text-4);margin-bottom:3px}
    .mcp-row .cost{font-size:11px;color:var(--text-6)}
    .tabs{display:flex;gap:6px;margin-bottom:14px}
    .tab{padding:7px 14px;background:var(--surface);border:1px solid var(--border);border-radius:6px;cursor:pointer;font-size:13px;color:var(--text-3)}
    .tab.active{background:var(--accent);color:#fff;border-color:var(--accent)}
    .hint{font-size:11px;color:var(--text-5);margin-top:5px;line-height:1.5}
    .toast{position:fixed;bottom:20px;right:20px;background:var(--ok);color:#fff;padding:10px 18px;border-radius:8px;font-size:13px;display:none;z-index:999}
    .toast.err{background:var(--err)}
    .cb-row{display:flex;align-items:flex-start;gap:8px;margin-bottom:12px}
    .cb-row input{margin-top:2px;flex-shrink:0}
    .cb-row .cb-label{font-size:13px;color:var(--text-2)}
    .cb-row .cb-help{font-size:11px;color:var(--text-5);margin-top:2px;line-height:1.4}
    .info-box{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin-bottom:20px;font-size:12px;color:var(--text-4);line-height:1.6}
    .info-box strong{color:var(--text-3)}
    pre#preview{background:var(--surface-deep);border:1px solid var(--border);border-radius:8px;padding:16px;font-size:11px;color:var(--code-fg);overflow:auto;height:520px;white-space:pre-wrap;font-family:'Courier New',monospace;line-height:1.5}
    .scope-badge{display:inline-block;font-size:10px;padding:2px 7px;border-radius:10px;margin-left:8px;vertical-align:middle;font-weight:500}
    .scope-badge.global{background:var(--badge-gb);color:var(--badge-gf)}
    .scope-badge.project{background:var(--badge-pb);color:var(--badge-pf)}
    .modal-overlay{position:fixed;inset:0;background:var(--overlay);z-index:200;display:flex;align-items:center;justify-content:center}
    .modal{background:var(--surface);border:1px solid var(--border);border-radius:12px;width:520px;max-height:520px;display:flex;flex-direction:column;box-shadow:var(--shadow)}
    .modal-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
    .modal-header h3{margin:0;font-size:14px;color:var(--text-strong)}
    .modal-header button{background:none;border:none;color:var(--text-4);font-size:20px;cursor:pointer;padding:0;line-height:1}
    .modal-header button:hover{color:var(--text-strong)}
    .modal-crumb{padding:10px 20px;border-bottom:1px solid var(--border-sub);font-family:monospace;font-size:12px;color:var(--text-4);background:var(--surface-deep);word-break:break-all}
    .modal-list{flex:1;overflow-y:auto;padding:8px}
    .modal-item{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:6px;cursor:pointer;font-size:13px;color:var(--text-2)}
    .modal-item:hover{background:var(--surface-hover);color:var(--text-strong)}
    .modal-item .icon{color:var(--accent);flex-shrink:0;font-size:15px}
    .modal-item.up .icon{color:var(--text-5)}
    .modal-footer{padding:12px 16px;border-top:1px solid var(--border);display:flex;gap:8px;justify-content:flex-end;align-items:center}
    .modal-footer .sel-path{flex:1;font-family:monospace;font-size:11px;color:var(--text-5);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .nav-footer{margin-top:auto;padding:12px 16px;border-top:1px solid var(--border)}
    .nav-brand{font-size:13px;color:var(--text-2);font-weight:600;margin-bottom:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-height:20px}
    .nav-controls{display:flex;gap:6px;margin-bottom:8px}
    .icon-btn{background:none;border:1px solid var(--border);color:var(--text-3);padding:5px 8px;font-size:14px;border-radius:5px;cursor:pointer;min-width:30px;font-family:inherit}
    .icon-btn:hover{background:var(--surface-hover);color:var(--text-strong)}
    .brand-edit{display:none;margin-top:4px}
    .brand-edit input{margin-bottom:6px;font-size:12px;padding:7px 10px}
    .brand-edit button{padding:6px 12px;font-size:12px;width:100%}
    .wizard-steps{display:none}
    .wizard-steps.active{display:block}
    .step-progress{display:flex;align-items:center;margin-bottom:24px;max-width:400px}
    .step-dot{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;flex-shrink:0;border:2px solid var(--border);color:var(--text-5);background:var(--surface)}
    .step-dot.active{background:var(--accent);border-color:var(--accent);color:#fff}
    .step-dot.done{background:var(--ok);border-color:var(--ok);color:#fff}
    .step-line{flex:1;height:2px;background:var(--border)}
    .step-line.done{background:var(--ok)}
    .step-actions{display:flex;justify-content:space-between;margin-top:24px}
    .step-actions.end{justify-content:flex-end}
    .np-field{margin-bottom:16px}
    .np-slug{font-size:11px;color:var(--text-5);margin-top:3px;font-family:monospace}
    .np-radio-group{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}
    .np-radio{padding:6px 14px;border:1px solid var(--border);border-radius:6px;cursor:pointer;font-size:13px;color:var(--text-3);background:var(--surface);user-select:none}
    .np-radio.active{background:var(--accent);border-color:var(--accent);color:#fff}
    .np-check-row{display:flex;align-items:center;gap:8px;margin-bottom:10px;font-size:13px;color:var(--text-2);cursor:pointer}
    .np-result{background:var(--surface-deep);border:1px solid var(--border);border-radius:6px;padding:10px 14px;margin-bottom:10px;font-family:'Courier New',monospace;font-size:12px;color:var(--code-fg)}
    .np-err{background:var(--err-border);border:1px solid var(--err);border-radius:6px;padding:10px 14px;font-size:12px;color:var(--err);margin-bottom:12px;line-height:1.5}
    .np-ok{color:var(--ok);font-weight:600;font-size:15px;margin-bottom:12px}
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
  <div class="nav-footer">
    <div class="nav-brand" id="brand-display">oculus-configs</div>
    <div class="nav-controls">
      <button class="icon-btn" id="theme-btn" onclick="toggleTheme()" title="Toggle theme">&#9788;</button>
      <button class="icon-btn" onclick="toggleBrandEdit()" title="Edit branding">&#9998;</button>
    </div>
    <div class="brand-edit" id="brand-edit">
      <input type="text" id="brand-name-input" placeholder="Display name">
      <input type="text" id="brand-logo-input" placeholder="Logo URL (optional)">
      <button onclick="saveBranding()">Save</button>
    </div>
  </div>
</nav>
<main>

<section id="dashboard" class="active">
  <h2>Config Status <span class="scope-badge global">global</span></h2>
  <p class="section-desc">Health of your global Claude Code config in <strong>~/.claude/</strong>. These settings apply to <strong>every project</strong> on this machine. Project-specific rules live in a <code>CLAUDE.md</code> inside each project folder.</p>
  <div class="status-grid" id="status-grid"><div class="card"><div class="val">Loading...</div></div></div>
</section>

<section id="wizard">
  <h2>CLAUDE.md <span class="scope-badge global">global</span></h2>
  <p class="section-desc">Your <strong>~/.claude/CLAUDE.md</strong> — Claude reads this at the start of <em>every</em> session on this machine. Use the Wizard to build it from a form, or Raw Edit to modify it directly.</p>
  <div class="tabs">
    <div class="tab active" id="tab-wizard" onclick="switchWizardMode('wizard',this)">Wizard</div>
    <div class="tab" id="tab-raw" onclick="switchWizardMode('raw',this)">Raw Edit</div>
  </div>

  <div id="wizard-form">
    <div class="two-col">
      <div>
        <div class="form-group">
          <span class="field-label">Active Plugins</span>
          <p class="field-help" style="margin-bottom:10px">Check the plugins you want Claude to load every session. Only enable what you actively use — each plugin adds overhead to every turn.</p>
          <div id="plugin-checks"></div>
        </div>
        <div class="form-group">
          <span class="field-label">Context compact threshold</span>
          <select id="threshold">
            <option value="60">60% — compact early, more headroom</option>
            <option value="70" selected>70% — recommended default</option>
            <option value="80">80% — squeeze more before compacting</option>
          </select>
          <p class="field-help">When Claude hits this % context usage, you get reminded to run <code>/compact</code>, which summarises the conversation so you can keep going. 70% is a safe default.</p>
        </div>
        <div class="form-group">
          <span class="field-label">Max MCP servers per session</span>
          <select id="maxmcp">
            <option value="2">2 servers — minimal overhead</option>
            <option value="3">3 servers</option>
            <option value="4" selected>4 servers — recommended max</option>
          </select>
          <p class="field-help">Each active MCP server costs 100–500 tokens every turn, even when unused. In practice most sessions only need GitHub + Context7.</p>
        </div>
        <div class="form-group">
          <span class="field-label">Personal notes (appended to file)</span>
          <textarea id="notes" placeholder="Examples:&#10;- Preferred language: Python 3.12&#10;- Always use type hints&#10;- Never use print() for debugging, use logging&#10;- I work solo, no PR review process needed"></textarea>
          <p class="field-help">Anything you always want Claude to know — language preferences, style rules, team conventions.</p>
        </div>
        <button onclick="saveClaudeMd()">Save to ~/.claude/CLAUDE.md</button>
      </div>
      <div>
        <span class="field-label">Live Preview</span>
        <p class="field-help" style="margin-bottom:8px">Exactly what will be written to disk when you click Save.</p>
        <pre id="preview"></pre>
      </div>
    </div>
  </div>

  <div id="wizard-raw" style="display:none">
    <p class="field-help" style="margin-bottom:12px">Editing <strong>~/.claude/CLAUDE.md</strong> directly. Changes are saved as-is — no formatting applied.</p>
    <textarea id="raw-editor" style="min-height:520px"></textarea>
    <button onclick="saveRawClaudeMd()" style="margin-top:12px">Save to ~/.claude/CLAUDE.md</button>
  </div>
</section>

<section id="mcp">
  <h2>MCP Setup <span class="scope-badge global">global</span></h2>
  <p class="section-desc"><strong>MCP (Model Context Protocol)</strong> connects Claude to external tools during your sessions. Without it, Claude can only see files you paste in. With it, Claude can read GitHub issues, create PRs, and look up live library docs — automatically. Each server costs tokens every turn it's active, so only enable what you need.</p>
  <div class="form-group" style="max-width:560px">
    <span class="field-label">GitHub Personal Access Token</span>
    <input type="text" id="gh-token" placeholder="ghp_...">
    <p class="hint">Create one at <strong>github.com → Settings → Developer settings → Personal access tokens → Tokens (classic)</strong>.<br>Required scopes: <code>repo</code>, <code>read:org</code>. No expiry needed for a personal machine.</p>
  </div>
  <h3>Servers</h3>
  <div id="mcp-list"></div>
  <button onclick="saveMcp()" style="margin-top:14px">Save MCP Config</button>
</section>

<section id="plugins">
  <h2>Plugins <span class="scope-badge global">global</span></h2>
  <p class="section-desc">Plugins add workflow skills to Claude Code — things like structured brainstorming, TDD enforcement, and code review checklists. <strong>Installed</strong> means the plugin files are on disk. <strong>Enabled</strong> means Claude actually loads them each session. You can install a plugin but leave it disabled to save overhead.</p>
  <div class="info-box" style="margin-bottom:16px">To install a plugin, open a Claude Code session and run the command shown in the Install Command column. You cannot install plugins from this UI — Claude Code handles that.</div>
  <table>
    <thead><tr><th>Plugin</th><th>What it does</th><th>Version</th><th>Installed</th><th>Enabled</th><th>Install Command</th></tr></thead>
    <tbody id="plugins-body"></tbody>
  </table>
</section>

<section id="templates">
  <h2>Project Templates <span class="scope-badge project">per-project</span></h2>
  <p class="section-desc">These templates live in <strong>~/Templates/claude-code-starter/</strong>. Edit them here to change what every new project starts with, then deploy them directly into any project folder.</p>
  <div class="tabs">
    <div class="tab active" onclick="switchTpl('template-claude',this)">CLAUDE.md starter</div>
    <div class="tab" onclick="switchTpl('template-decisions',this)">DECISIONS.md starter</div>
  </div>
  <textarea id="tpl-editor" style="min-height:380px"></textarea>
  <div style="display:flex;gap:10px;margin-top:12px">
    <button onclick="saveTpl()">Save Template</button>
    <button class="sec" onclick="document.getElementById('deploy-panel').style.display=document.getElementById('deploy-panel').style.display==='none'?'block':'none'">Copy to Project...</button>
  </div>
  <div id="deploy-panel" style="display:none;margin-top:16px;padding:16px;background:#141414;border:1px solid #2a2a2a;border-radius:8px">
    <span class="field-label">Project folder path</span>
    <p class="field-help" style="margin-bottom:10px">CLAUDE.md starter → <code>{folder}/CLAUDE.md</code> &nbsp;·&nbsp; DECISIONS.md starter → <code>{folder}/docs/DECISIONS.md</code></p>
    <div style="display:flex;gap:8px;align-items:flex-start">
      <input type="text" id="deploy-path" placeholder="/home/peyton/repos/my-project" style="flex:1">
      <button class="sec" onclick="openBrowse()" style="flex-shrink:0;white-space:nowrap">Browse...</button>
      <button onclick="deployTpl()" style="flex-shrink:0;white-space:nowrap">Copy Now</button>
    </div>
    <p class="hint" style="margin-top:8px">The folder must already exist. Subdirectories (like docs/) are created automatically. Existing files are overwritten.</p>
  </div>
</section>

</main>

<div class="modal-overlay" id="browse-modal" style="display:none" onclick="if(event.target===this)closeBrowse()">
  <div class="modal">
    <div class="modal-header">
      <h3>Select Project Folder</h3>
      <button onclick="closeBrowse()">&#x2715;</button>
    </div>
    <div class="modal-crumb" id="browse-crumb">/</div>
    <div class="modal-list" id="browse-list"></div>
    <div class="modal-footer">
      <span class="sel-path" id="browse-sel"></span>
      <button class="sec" onclick="closeBrowse()">Cancel</button>
      <button onclick="confirmBrowse()">Select This Folder</button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let plugData={};let mcpData={};let curTpl='template-claude';let brandData={};

function toggleTheme(){
  const isLight=document.body.classList.toggle('light');
  document.getElementById('theme-btn').textContent=isLight?'\u263D':'\u2600';
  localStorage.setItem('theme',isLight?'light':'dark');
}

async function loadBranding(){
  brandData=await api('/api/branding');
  applyBranding(brandData);
}

function applyBranding(b){
  const name=b.name||'oculus-configs';
  document.getElementById('brand-display').textContent=name;
  document.title=name;
}

function toggleBrandEdit(){
  const el=document.getElementById('brand-edit');
  const visible=el.style.display==='block';
  if(!visible){
    document.getElementById('brand-name-input').value=brandData.name||'';
    document.getElementById('brand-logo-input').value=brandData.logo||'';
  }
  el.style.display=visible?'none':'block';
}

async function saveBranding(){
  const b={name:document.getElementById('brand-name-input').value.trim(),logo:document.getElementById('brand-logo-input').value.trim()};
  const d=await api('/api/branding','POST',b);
  if(d.ok){brandData=b;applyBranding(b);document.getElementById('brand-edit').style.display='none';toast('Branding saved');}
  else toast('Error: '+d.error,true);
}

function nav(id,el){
  document.querySelectorAll('section').forEach(s=>s.classList.remove('active'));
  document.querySelectorAll('nav a').forEach(a=>a.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
    if(id==='dashboard')loadDash();
  else if(id==='wizard')loadWizard();
  else if(id==='mcp')loadMcp();
  else if(id==='plugins')loadPlugins();
  else if(id==='templates')loadTpl('template-claude');
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
    `<div class="card ${i.status!=='ok'?i.status:''}">
      <div class="lbl">${i.label}</div>
      ${i.desc?`<div class="card-desc">${i.desc}</div>`:''}
      <div class="val"><span class="dot ${i.status}"></span>${i.message}</div>
      ${i.fix?`<div class="fix">${i.fix}</div>`:''}
    </div>`
  ).join('');
}

function switchWizardMode(mode,el){
  document.querySelectorAll('.tabs .tab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  if(mode==='raw'){
    document.getElementById('wizard-form').style.display='none';
    document.getElementById('wizard-raw').style.display='block';
    api('/api/config/CLAUDE.md').then(d=>{
      document.getElementById('raw-editor').value=d.content||'';
    });
  } else {
    document.getElementById('wizard-raw').style.display='none';
    document.getElementById('wizard-form').style.display='block';
  }
}

async function saveRawClaudeMd(){
  const content=document.getElementById('raw-editor').value;
  const d=await api('/api/config/CLAUDE.md','POST',{content});
  d.ok?toast('Saved ~/.claude/CLAUDE.md'):toast('Error: '+d.error,true);
}

async function loadWizard(){
  plugData=await api('/api/plugins');
  document.getElementById('plugin-checks').innerHTML=plugData.known.map(p=>
    `<div class="cb-row">
      <input type="checkbox" value="${p.id}" ${p.installed?'checked':''}>
      <div>
        <div class="cb-label">${p.label}${!p.installed?' <span style="color:#555;font-size:11px">(not installed)</span>':''}</div>
        <div class="cb-help">${p.description}</div>
      </div>
    </div>`
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
    return p?`### ${p.label} (${p.id}) — ENABLED\\n- ${p.description}`:'';
  }).filter(Boolean).join('\\n\\n');
  document.getElementById('preview').textContent=
`# Global Claude Code Configuration
**Scope**: All projects on this machine

## Active Plugins

${plugLines||'(no plugins selected)'}

## Token Discipline (HIGH PRIORITY)

1. **One task per session** — don't reuse for unrelated work
2. **Check context at /usage** — compact or clear when approaching ${thr}%
3. **Use /compact selectively**: \\`/compact focus on [active feature]\\`
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
- [ ] \\`.claude/HANDOFF.md\\` updated with next steps
- [ ] Push to remote if checkpoint is meaningful
${notes?'\\n## Notes\\n\\n'+notes:''}
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
    {id:'github',name:'GitHub',desc:'Lets Claude read issues, create PRs, search code, and comment — without you pasting anything in. Requires a token.',cost:'~200–400 tokens/turn when active'},
    {id:'context7',name:'Context7',desc:'Pulls live, version-accurate docs for libraries in use. Prevents Claude from hallucinating outdated API signatures. No token needed.',cost:'~100–300 tokens/turn when queried'}
  ];
  document.getElementById('mcp-list').innerHTML=servers.map(s=>
    `<div class="mcp-row">
      <div class="inf">
        <div class="name">${s.name}</div>
        <div class="mcp-desc">${s.desc}</div>
        <div class="cost">${s.cost}</div>
      </div>
      <label class="toggle"><input type="checkbox" id="mcp-${s.id}" ${mcpData.servers?.[s.id]?'checked':''}><span class="slider"></span></label>
    </div>`
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
      <td style="color:#666;font-size:12px">${p.description}</td>
      <td style="color:#555">${p.version||'—'}</td>
      <td><span class="dot ${p.installed?'ok':'err'}" style="display:inline-block;margin-right:6px"></span>${p.installed?'Yes':'No'}</td>
      <td>${p.installed?`<label class="toggle"><input type="checkbox" ${p.enabled?'checked':''} onchange="togglePlugin('${p.id}',this.checked)"><span class="slider"></span></label>`:'—'}</td>
      <td>${!p.installed?`<span class="code">${p.install}</span>`:'<span style="color:#444">already installed</span>'}</td>
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

async function deployTpl(){
  const dest=document.getElementById('deploy-path').value.trim();
  if(!dest){toast('Enter a project folder path',true);return;}
  const content=document.getElementById('tpl-editor').value;
  const d=await api('/api/templates/deploy','POST',{file:curTpl,dest,content});
  d.ok?toast('Copied to '+d.path):toast('Error: '+d.error,true);
}

let browseData={};
function openBrowse(){
  document.getElementById('browse-modal').style.display='flex';
  navigateBrowse('~');
}
function closeBrowse(){
  document.getElementById('browse-modal').style.display='none';
}
function confirmBrowse(){
  const p=browseData.path||'';
  if(p)document.getElementById('deploy-path').value=p;
  closeBrowse();
}
async function navigateBrowse(path){
  const d=await api('/api/browse?path='+encodeURIComponent(path));
  browseData=d;
  document.getElementById('browse-crumb').textContent=d.path||path;
  document.getElementById('browse-sel').textContent=d.path||path;
  const list=document.getElementById('browse-list');
  if(d.error&&!d.dirs){
    list.innerHTML='<div style="padding:16px;color:#ef4444;font-size:13px">'+d.error+'</div>';
    return;
  }
  const items=[];
  if(d.parent)items.push({path:d.parent,label:'.. (up a level)',cls:'up',icon:'&#x2191;'});
  (d.dirs||[]).forEach(function(name){
    items.push({path:(d.path==='/'?'':d.path)+'/'+name,label:name,cls:'',icon:'&#x1F4C1;'});
  });
  list.innerHTML=items.length
    ? items.map(function(i){return '<div class="modal-item '+i.cls+'" data-path="'+i.path+'"><span class="icon">'+i.icon+'</span>'+i.label+'</div>';}).join('')
    : '<div style="padding:16px;color:#444;font-size:13px;text-align:center">No subdirectories</div>';
  list.querySelectorAll('.modal-item').forEach(function(el){
    el.addEventListener('click',function(){navigateBrowse(this.dataset.path);});
  });
}

(function(){var t=localStorage.getItem('theme');if(t==='light'){document.body.classList.add('light');document.getElementById('theme-btn').textContent='\u263d';}})();
loadBranding();
loadDash();
</script>
</body>
</html>"""


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
        elif path == "/api/branding":
            self._send_json(get_branding())
        elif path == "/api/browse":
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            browse_path = qs.get("path", [str(Path.home())])[0]
            self._send_json(browse_dir(browse_path))
        elif path == "/api/which/gh":
            self._send_json(which_gh())
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
        elif path == "/api/branding":
            self._send_json(write_branding(self._read_body()))
        elif path == "/api/templates/deploy":
            body = self._read_body()
            self._send_json(deploy_template(body.get("file", ""), body.get("dest", ""), body.get("content", "")))
        elif path == "/api/projects/create":
            body = self._read_body()
            self._send_json(create_project(
                body.get("name", ""),
                body.get("parent", ""),
                body.get("templates", [])
            ))
        elif path == "/api/projects/github":
            body = self._read_body()
            self._send_json(github_project(
                body.get("path", ""),
                body.get("repo_name", ""),
                body.get("private", True)
            ))
        elif path == "/api/projects/remote":
            body = self._read_body()
            self._send_json(remote_project(
                body.get("path", ""),
                body.get("remote_url", "")
            ))
        elif path == "/api/projects/open-vscode":
            body = self._read_body()
            self._send_json(open_vscode(body.get("path", "")))
        else:
            self._send_json({"error": "Not found"}, 404)


# ── Entry point ───────────────────────────────────────────────────────────────

def _open_browser(url: str):
    import subprocess
    import platform
    uname = platform.uname()
    if "microsoft" in uname.release.lower() or "wsl" in uname.release.lower():
        try:
            subprocess.Popen(["/mnt/c/Windows/System32/cmd.exe", "/c", "start", url],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except Exception:
            pass
    webbrowser.open(url)


def main():
    url = f"http://localhost:{PORT}"
    server = HTTPServer(("localhost", PORT), ConfigHandler)
    threading.Timer(0.5, lambda: _open_browser(url)).start()
    print(f"oculus-configs UI → {url}")
    print("Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
