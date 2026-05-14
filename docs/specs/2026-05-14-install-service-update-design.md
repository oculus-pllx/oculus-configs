# Install, Service & Self-Update Design

**Date**: 2026-05-14  
**Status**: Approved  
**ADRs**: 001 (stdlib only), 007 (subprocess for system commands)

---

## Overview

Make `configure.py` a first-class installed tool. After `bash install.sh`, the user has:

1. A `configure` executable in `~/.local/bin/` (in PATH)
2. A background service that starts on login (systemd on Linux/WSL2, launchd on macOS)
3. A self-update mechanism: the Dashboard shows available commits and an "Apply Update" button that pulls, reinstalls the binary, and restarts the service

No new files beyond the service unit. No pip dependencies. No new nav section — update status lives on the Dashboard.

---

## Architecture

### Approach

**Single install.sh does everything** (Approach A). One script, one run. Repo path recorded in `~/.claude/settings.json` at install time so the running server always knows where to `git pull` from without hardcoding.

### Platform Support

| Platform | Detection | Service mechanism |
|----------|-----------|-------------------|
| WSL2 | `uname -r` contains `microsoft` | systemd user service |
| Linux | `uname -s == Linux` | systemd user service |
| macOS | `uname -s == Darwin` | launchd user agent |
| Unknown | fallback | prints manual-run instructions; no hard failure |

### Data Flow — Update

```
Dashboard load → GET /api/update/check
  → git fetch (network)
  → git rev-list HEAD..origin/main --count
  → {"available": true, "commits": N, "latest": "<sha>"}

User clicks "Apply Update" → POST /api/update/apply
  → git pull (in repo_path)
  → shutil.copy2(repo/configure.py → ~/.local/bin/configure)
  → systemctl --user restart oculus-configure  (Linux/WSL2)
     OR launchctl kickstart -k gui/<uid>/com.oculus.configure  (macOS)
  → {"ok": true, "restarting": true}

Frontend receives restarting:true
  → polls GET /api/status every 1s
  → reloads page when server responds
```

---

## Components

### install.sh — New Sections (§5–§7)

**§5 — Install binary**

```bash
mkdir -p "$HOME/.local/bin"
cp "$REPO_DIR/configure.py" "$HOME/.local/bin/configure"
chmod +x "$HOME/.local/bin/configure"
# Warn if ~/.local/bin is not in PATH
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
  echo "[warn] ~/.local/bin is not in your PATH"
  echo "       Add: export PATH=\"\$HOME/.local/bin:\$PATH\" to ~/.bashrc or ~/.zshrc"
fi
```

**§6 — Record repo path**

Uses Python (already required) to merge into `settings.json` without overwriting existing keys:

```python
import json, pathlib
p = pathlib.Path('~/.claude/settings.json').expanduser()
d = json.loads(p.read_text()) if p.exists() else {}
d.setdefault('oculus', {})['repo_path'] = '/path/to/repo'
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(d, indent=2))
```

**§7 — Service setup**

Platform detected via `uname -s` / `uname -r`. If service already exists, old one is stopped, unit file overwritten, service restarted.

*Linux/WSL2 — systemd user service* at `~/.config/systemd/user/oculus-configure.service`:

```ini
[Unit]
Description=oculus-configs UI
After=network.target

[Service]
ExecStart=%h/.local/bin/configure
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Enabled with:
```bash
systemctl --user daemon-reload
systemctl --user enable oculus-configure
systemctl --user start oculus-configure
```

*macOS — launchd user agent* at `~/Library/LaunchAgents/com.oculus.configure.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.oculus.configure</string>
  <key>ProgramArguments</key>
  <array><string>/Users/USERNAME/.local/bin/configure</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/oculus-configure.log</string>
  <key>StandardErrorPath</key><string>/tmp/oculus-configure.log</string>
</dict>
</plist>
```

Loaded with:
```bash
launchctl load ~/Library/LaunchAgents/com.oculus.configure.plist
```

### configure.py — New Backend Functions

```python
def get_repo_path() -> str | None
def check_update() -> dict          # GET /api/update/check
def apply_update() -> dict          # POST /api/update/apply
def _restart_service() -> dict      # called by apply_update
def get_version_info() -> dict      # GET /api/update/version
```

**`get_repo_path()`** — reads `settings.json`, returns `oculus.repo_path` or `None`.

**`check_update()`** — requires `repo_path` set and `git` in PATH. Runs `git fetch` then `git rev-list HEAD..origin/main --count`. Returns:
```json
{"available": true, "commits": 3, "latest": "a1b2c3d"}
```
or `{"available": false, "commits": 0}` or `{"available": false, "error": "..."}`.

**`apply_update()`** — sequentially: `git pull` → copy binary → restart service. Aborts at first failure; does not restart if copy fails. Returns `{"ok": true, "restarting": true/false}` or `{"ok": false, "error": "..."}`.

**`_restart_service()`** — platform-aware:
- WSL2/Linux: `systemctl --user restart oculus-configure`
- macOS: `launchctl kickstart -k gui/<uid>/com.oculus.configure`
- Unknown: no-op, returns `{"restarting": false}`

**`get_version_info()`** — runs `git -C repo_path log -1 --format="%h %ai %s"`, returns `{"sha": "...", "date": "...", "message": "..."}` or `{"sha": "unknown"}` on failure.

### configure.py — New HTTP Endpoints

| Method | Path | Handler |
|--------|------|---------|
| GET | `/api/update/check` | `check_update()` |
| GET | `/api/update/version` | `get_version_info()` |
| POST | `/api/update/apply` | `apply_update()` |

### GUI — Dashboard Update Card

Loaded alongside existing status cards. State machine:

| State | Visual |
|-------|--------|
| loading | spinner · "Checking for updates…" |
| up-to-date | ✓ green · "Up to date" · sha + date |
| available | ⬆ amber · "N commits available" · "Apply Update" button |
| error | ⚠ warn · error message · "Check again" button |
| updating | spinner · "Applying update…" button disabled |
| restarting | "Restarting…" · polls `/api/status` every 1s · reloads page on response |

"Check for updates" button always visible — manual re-fetch without page reload.

---

## Error Handling

| Failure | Behaviour |
|---------|-----------|
| `repo_path` not set | `check_update` returns `{"available": false, "error": "repo not configured"}` — warn card |
| No network / git fetch fails | `check_update` returns error — warn card; does not block Dashboard |
| `git pull` fails | `apply_update` returns `{"ok": false}` — no binary copy, no restart; safe to retry |
| Binary copy fails after pull | Returns `{"ok": false, "error": "copy failed — repo updated, binary unchanged"}` — skips restart |
| Service restart fails | Logs error; returns `{"ok": true, "restarting": false}` — GUI tells user to restart manually |
| Server not running as service | `_restart_service` is a no-op; `restarting: false` — GUI skips reconnect polling |

---

## Testing

New test classes in `tests/test_configure.py` (all subprocess calls mocked):

| Class | Tests |
|-------|-------|
| `TestGetRepoPath` | path present; path missing; settings.json absent |
| `TestCheckUpdate` | up to date; commits available; repo_path missing; git not found |
| `TestApplyUpdate` | success (restarting); pull failure aborts; copy failure skips restart |
| `TestRestartService` | Linux/WSL2 command; macOS command; unknown platform no-op |

`install.sh` is not unit-tested. Manual test checklist (included in plan):
- Fresh VM: clone → `bash install.sh` → `configure` command works → browser opens
- Re-run install.sh: service restarts cleanly, no duplicate units
- macOS: plist written → `launchctl list | grep oculus` shows service
- Update: push a commit to remote → Dashboard shows badge → Apply → page reloads

---

## Scope / Out of Scope

**In scope:**
- `install.sh` §5–§7 (binary, repo_path, service)
- `check_update`, `apply_update`, `get_version_info`, `get_repo_path`, `_restart_service`
- Three new API endpoints
- Dashboard update card
- Unit tests for all new backend functions

**Out of scope:**
- Windows native (non-WSL) service — Task Scheduler setup is materially different; deferred
- Rollback on failed update
- Changelog display (beyond commit count)
- Notification when update is available without opening the GUI
