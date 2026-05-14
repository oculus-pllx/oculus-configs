# Install, Service & Self-Update Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `configure.py` a first-class installed tool — `bash install.sh` puts a `configure` binary in PATH, sets up a login service (systemd/launchd), and equips the Dashboard with an update card that pulls and reinstalls on demand.

**Architecture:** `install.sh` gains three new sections (§5 binary, §6 repo_path, §7 service). `configure.py` gains four backend functions (`get_repo_path`, `check_update`, `apply_update`, `_restart_service`) wired to three new endpoints. The Dashboard update card polls those endpoints and handles the reconnect cycle after restart.

**Tech Stack:** Python 3 stdlib (`platform`, `shutil`, `subprocess`), Bash, systemd user services (Linux/WSL2), launchd user agents (macOS), vanilla JS.

---

## File Map

- **Modify:** `configure.py`
  - Add `import platform` to top-level imports (~line 10)
  - Add `get_repo_path()`, `get_version_info()`, `check_update()`, `_restart_service()`, `apply_update()` after `fs_move` (~line 395)
  - Add 3 new routes to `do_GET` and `do_POST`
  - Add update card HTML to dashboard section (~line 569)
  - Add `loadUpdateCard()`, `applyUpdate()`, `pollReconnect()` JS functions before closing `</script>`
  - Call `loadUpdateCard()` from `loadDash()`
- **Modify:** `tests/test_configure.py` — add `TestGetRepoPath`, `TestCheckUpdate`, `TestRestartService`, `TestApplyUpdate`
- **Modify:** `install.sh` — add §5 (binary), §6 (repo_path), §7 (service)

---

## Task 1: Backend — get_repo_path + get_version_info

**Files:**
- Modify: `configure.py` (add `import platform`; add functions after `fs_move` ~line 395)
- Modify: `tests/test_configure.py` (add `TestGetRepoPath`)

- [ ] **Step 1: Add `import platform` to top-level imports**

After `import urllib.parse` (~line 10), add:

```python
import platform
```

- [ ] **Step 2: Write failing tests for get_repo_path**

Add before `class TestHtmlJs`:

```python
class TestGetRepoPath(unittest.TestCase):
    def test_returns_path_when_present(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            settings = Path(tmp) / "settings.json"
            settings.write_text(json.dumps({"oculus": {"repo_path": "/some/repo"}}))
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": settings}):
                result = configure.get_repo_path()
        self.assertEqual(result, "/some/repo")

    def test_returns_none_when_key_missing(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            settings = Path(tmp) / "settings.json"
            settings.write_text(json.dumps({}))
            with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": settings}):
                result = configure.get_repo_path()
        self.assertIsNone(result)

    def test_returns_none_when_file_absent(self):
        import configure
        with patch.object(configure, "CONFIG_PATHS", {**configure.CONFIG_PATHS, "settings": Path("/nonexistent/settings.json")}):
            result = configure.get_repo_path()
        self.assertIsNone(result)
```

- [ ] **Step 3: Run to verify they fail**

```
python3 -m unittest tests.test_configure.TestGetRepoPath -v
```

Expected: FAIL — `AttributeError: module 'configure' has no attribute 'get_repo_path'`

- [ ] **Step 4: Implement get_repo_path and get_version_info**

After `fs_move` (~line 395, before `TEMPLATE_DEST`), add:

```python
def get_repo_path() -> str | None:
    settings_path = CONFIG_PATHS["settings"]
    try:
        data = json.loads(settings_path.read_text()) if settings_path.exists() else {}
        return data.get("oculus", {}).get("repo_path")
    except Exception:
        return None


def get_version_info() -> dict:
    repo = get_repo_path()
    if not repo:
        return {"sha": "unknown", "date": "unknown", "message": "repo not configured"}
    try:
        r = subprocess.run(
            ["git", "log", "-1", "--format=%h\t%ai\t%s"],
            cwd=repo, capture_output=True, text=True, timeout=5
        )
        if r.returncode != 0 or not r.stdout.strip():
            return {"sha": "unknown", "date": "unknown", "message": "git error"}
        parts = r.stdout.strip().split("\t", 2)
        return {
            "sha": parts[0],
            "date": parts[1][:10] if len(parts) > 1 else "unknown",
            "message": parts[2] if len(parts) > 2 else "",
        }
    except Exception as e:
        return {"sha": "unknown", "date": "unknown", "message": str(e)}
```

- [ ] **Step 5: Wire GET /api/update/version in do_GET**

In `do_GET`, after `elif path == "/api/which/gh":` and before the final `else:`:

```python
        elif path == "/api/update/version":
            self._send_json(get_version_info())
```

- [ ] **Step 6: Run TestGetRepoPath to verify it passes**

```
python3 -m unittest tests.test_configure.TestGetRepoPath -v
```

Expected: 3 tests PASS

- [ ] **Step 7: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add get_repo_path + get_version_info + /api/update/version"
```

---

## Task 2: Backend — check_update

**Files:**
- Modify: `configure.py` (add `check_update` after `get_version_info`)
- Modify: `tests/test_configure.py` (add `TestCheckUpdate`)

- [ ] **Step 1: Write failing tests**

Add after `TestGetRepoPath`:

```python
class TestCheckUpdate(unittest.TestCase):
    def test_no_repo_path_returns_error(self):
        import configure
        with patch.object(configure, "get_repo_path", return_value=None):
            result = configure.check_update()
        self.assertFalse(result["available"])
        self.assertIn("error", result)

    def test_git_not_found_returns_error(self):
        import configure
        with patch.object(configure, "get_repo_path", return_value="/repo"):
            with patch("configure.shutil.which", return_value=None):
                result = configure.check_update()
        self.assertFalse(result["available"])
        self.assertIn("error", result)

    def test_up_to_date(self):
        import configure
        from unittest.mock import MagicMock
        with patch.object(configure, "get_repo_path", return_value="/repo"):
            with patch("configure.shutil.which", return_value="/usr/bin/git"):
                with patch("configure.subprocess.run") as mock_run:
                    mock_run.side_effect = [
                        MagicMock(returncode=0, stdout="", stderr=""),      # git fetch
                        MagicMock(returncode=0, stdout="0\n", stderr=""),   # rev-list count
                        MagicMock(returncode=0, stdout="abc1234\n", stderr=""),  # rev-parse
                    ]
                    result = configure.check_update()
        self.assertFalse(result["available"])
        self.assertEqual(result["commits"], 0)

    def test_commits_available(self):
        import configure
        from unittest.mock import MagicMock
        with patch.object(configure, "get_repo_path", return_value="/repo"):
            with patch("configure.shutil.which", return_value="/usr/bin/git"):
                with patch("configure.subprocess.run") as mock_run:
                    mock_run.side_effect = [
                        MagicMock(returncode=0, stdout="", stderr=""),       # git fetch
                        MagicMock(returncode=0, stdout="3\n", stderr=""),    # rev-list count
                        MagicMock(returncode=0, stdout="abc1234\n", stderr=""),  # rev-parse
                    ]
                    result = configure.check_update()
        self.assertTrue(result["available"])
        self.assertEqual(result["commits"], 3)
        self.assertEqual(result["latest"], "abc1234")
```

- [ ] **Step 2: Run to verify they fail**

```
python3 -m unittest tests.test_configure.TestCheckUpdate -v
```

Expected: FAIL — `AttributeError: module 'configure' has no attribute 'check_update'`

- [ ] **Step 3: Implement check_update**

Add after `get_version_info`:

```python
def check_update() -> dict:
    repo = get_repo_path()
    if not repo:
        return {"available": False, "error": "repo not configured — run install.sh again"}
    if not shutil.which("git"):
        return {"available": False, "error": "git not found in PATH"}
    try:
        r = subprocess.run(
            ["git", "fetch", "origin"], cwd=repo, capture_output=True, text=True, timeout=15
        )
        if r.returncode != 0:
            return {"available": False, "error": r.stderr.strip() or "git fetch failed"}
        r = subprocess.run(
            ["git", "rev-list", "HEAD..origin/main", "--count"],
            cwd=repo, capture_output=True, text=True, timeout=5
        )
        count = int(r.stdout.strip()) if r.returncode == 0 and r.stdout.strip().isdigit() else 0
        r2 = subprocess.run(
            ["git", "rev-parse", "--short", "origin/main"],
            cwd=repo, capture_output=True, text=True, timeout=5
        )
        latest = r2.stdout.strip() if r2.returncode == 0 else "unknown"
        return {"available": count > 0, "commits": count, "latest": latest}
    except subprocess.TimeoutExpired:
        return {"available": False, "error": "git fetch timed out"}
    except Exception as e:
        return {"available": False, "error": str(e)}
```

- [ ] **Step 4: Wire GET /api/update/check in do_GET**

After the `elif path == "/api/update/version":` line, add:

```python
        elif path == "/api/update/check":
            self._send_json(check_update())
```

- [ ] **Step 5: Run tests to verify they pass**

```
python3 -m unittest tests.test_configure.TestCheckUpdate -v
```

Expected: 4 tests PASS

- [ ] **Step 6: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add check_update backend + /api/update/check"
```

---

## Task 3: Backend — _restart_service

**Files:**
- Modify: `configure.py` (add `_restart_service` after `check_update`)
- Modify: `tests/test_configure.py` (add `TestRestartService`)

- [ ] **Step 1: Write failing tests**

Add after `TestCheckUpdate`. Note: `MagicMock` must be imported — add `from unittest.mock import patch, MagicMock` at the top of the test file (replace the existing `from unittest.mock import patch`).

```python
class TestRestartService(unittest.TestCase):
    def test_linux_uses_systemctl(self):
        import configure
        from unittest.mock import MagicMock
        with patch("configure.platform.system", return_value="Linux"):
            with patch("configure.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stderr="")
                result = configure._restart_service()
        self.assertTrue(result["restarting"])
        cmd = mock_run.call_args[0][0]
        self.assertIn("systemctl", cmd)
        self.assertIn("oculus-configure", cmd)

    def test_macos_uses_launchctl(self):
        import configure
        from unittest.mock import MagicMock
        with patch("configure.platform.system", return_value="Darwin"):
            with patch("configure.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stderr="")
                result = configure._restart_service()
        self.assertTrue(result["restarting"])
        cmd = mock_run.call_args[0][0]
        self.assertIn("launchctl", cmd)

    def test_unknown_platform_no_restart(self):
        import configure
        with patch("configure.platform.system", return_value="Windows"):
            result = configure._restart_service()
        self.assertFalse(result["restarting"])
        self.assertIsNone(result["error"])
```

Also update the import at the top of `tests/test_configure.py`:

```python
from unittest.mock import patch, MagicMock
```

- [ ] **Step 2: Run to verify they fail**

```
python3 -m unittest tests.test_configure.TestRestartService -v
```

Expected: FAIL — `AttributeError: module 'configure' has no attribute '_restart_service'`

- [ ] **Step 3: Implement _restart_service**

Add after `check_update`:

```python
def _restart_service() -> dict:
    system = platform.system()
    try:
        if system == "Linux":
            r = subprocess.run(
                ["systemctl", "--user", "restart", "oculus-configure"],
                capture_output=True, text=True, timeout=10
            )
            return {"restarting": r.returncode == 0, "error": r.stderr.strip() if r.returncode != 0 else None}
        elif system == "Darwin":
            uid = str(os.getuid())
            r = subprocess.run(
                ["launchctl", "kickstart", "-k", f"gui/{uid}/com.oculus.configure"],
                capture_output=True, text=True, timeout=10
            )
            return {"restarting": r.returncode == 0, "error": r.stderr.strip() if r.returncode != 0 else None}
        else:
            return {"restarting": False, "error": None}
    except Exception as e:
        return {"restarting": False, "error": str(e)}
```

- [ ] **Step 4: Run tests to verify they pass**

```
python3 -m unittest tests.test_configure.TestRestartService -v
```

Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add _restart_service (systemd/launchd/no-op)"
```

---

## Task 4: Backend — apply_update + wire POST endpoint

**Files:**
- Modify: `configure.py` (add `apply_update` after `_restart_service`; add POST route)
- Modify: `tests/test_configure.py` (add `TestApplyUpdate`)

- [ ] **Step 1: Write failing tests**

Add after `TestRestartService`:

```python
class TestApplyUpdate(unittest.TestCase):
    def test_success(self):
        import configure
        from unittest.mock import MagicMock
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            (repo / "configure.py").write_text("# fake")
            with patch.object(configure, "get_repo_path", return_value=str(repo)):
                with patch("configure.subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                    with patch.object(configure, "_restart_service", return_value={"restarting": True, "error": None}):
                        with patch("configure.shutil.copy2"):
                            result = configure.apply_update()
        self.assertTrue(result["ok"])
        self.assertTrue(result["restarting"])

    def test_pull_failure_aborts_before_copy(self):
        import configure
        from unittest.mock import MagicMock
        with patch.object(configure, "get_repo_path", return_value="/repo"):
            with patch("configure.subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="merge conflict")
                with patch("configure.shutil.copy2") as mock_copy:
                    result = configure.apply_update()
        self.assertFalse(result["ok"])
        self.assertIn("pull failed", result["error"])
        mock_copy.assert_not_called()

    def test_copy_failure_skips_restart(self):
        import configure
        from unittest.mock import MagicMock
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            (repo / "configure.py").write_text("# fake")
            with patch.object(configure, "get_repo_path", return_value=str(repo)):
                with patch("configure.subprocess.run") as mock_run:
                    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
                    with patch("configure.shutil.copy2", side_effect=PermissionError("denied")):
                        with patch.object(configure, "_restart_service") as mock_restart:
                            result = configure.apply_update()
        self.assertFalse(result["ok"])
        self.assertIn("copy failed", result["error"])
        mock_restart.assert_not_called()
```

- [ ] **Step 2: Run to verify they fail**

```
python3 -m unittest tests.test_configure.TestApplyUpdate -v
```

Expected: FAIL — `AttributeError: module 'configure' has no attribute 'apply_update'`

- [ ] **Step 3: Implement apply_update**

Add after `_restart_service`:

```python
def apply_update() -> dict:
    repo = get_repo_path()
    if not repo:
        return {"ok": False, "error": "repo not configured — run install.sh again"}
    try:
        r = subprocess.run(
            ["git", "pull"], cwd=repo, capture_output=True, text=True, timeout=30
        )
        if r.returncode != 0:
            return {"ok": False, "error": f"git pull failed: {r.stderr.strip() or r.stdout.strip()}"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "git pull timed out"}
    src = Path(repo) / "configure.py"
    dest = Path.home() / ".local" / "bin" / "configure"
    try:
        shutil.copy2(str(src), str(dest))
    except Exception as e:
        return {"ok": False, "error": f"copy failed — repo updated, binary unchanged: {e}"}
    restart = _restart_service()
    return {"ok": True, "restarting": restart["restarting"]}
```

- [ ] **Step 4: Wire POST /api/update/apply in do_POST**

In `do_POST`, before the final `else:` clause, add:

```python
        elif path == "/api/update/apply":
            self._send_json(apply_update())
```

- [ ] **Step 5: Run full test suite**

```
python3 -m unittest tests.test_configure -v
```

Expected: all tests PASS (should be ~46 tests)

- [ ] **Step 6: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add apply_update + /api/update/apply endpoint"
```

---

## Task 5: Dashboard update card

**Files:**
- Modify: `configure.py` (dashboard HTML ~line 569; JS `loadDash` ~line 860; add new JS functions before closing `</script>`)

- [ ] **Step 1: Add update card HTML to dashboard section**

Replace the dashboard section:

```python
<section id="dashboard" class="active">
  <h2>Config Status <span class="scope-badge global">global</span></h2>
  <p class="section-desc">Health of your global Claude Code config in <strong>~/.claude/</strong>. These settings apply to <strong>every project</strong> on this machine. Project-specific rules live in a <code>CLAUDE.md</code> inside each project folder.</p>
  <div class="status-grid" id="status-grid"><div class="card"><div class="val">Loading...</div></div></div>
</section>
```

With:

```html
<section id="dashboard" class="active">
  <h2>Config Status <span class="scope-badge global">global</span></h2>
  <p class="section-desc">Health of your global Claude Code config in <strong>~/.claude/</strong>. These settings apply to <strong>every project</strong> on this machine. Project-specific rules live in a <code>CLAUDE.md</code> inside each project folder.</p>
  <div class="status-grid" id="status-grid"><div class="card"><div class="val">Loading...</div></div></div>
  <div id="update-card" class="card" style="margin-top:16px;max-width:480px">
    <div class="lbl">oculus-configs</div>
    <div class="val" id="update-val"><span class="dot"></span> Checking for updates...</div>
    <div id="update-actions" style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap"></div>
  </div>
</section>
```

- [ ] **Step 2: Update loadDash() to call loadUpdateCard()**

Replace:

```javascript
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
```

With:

```javascript
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
  loadUpdateCard();
}
```

- [ ] **Step 3: Add loadUpdateCard, applyUpdate, pollReconnect JS functions**

Before the closing `</script>` tag (just before the `(function(){...})()` IIFE at the bottom), add:

```javascript
async function loadUpdateCard(){
  const val=document.getElementById('update-val');
  const actions=document.getElementById('update-actions');
  val.innerHTML='<span class="dot"></span> Checking...';
  actions.innerHTML='';
  const v=await api('/api/update/version');
  const ver=v.sha!=='unknown'?`${v.sha} · ${v.date}`:'version unknown';
  const d=await api('/api/update/check');
  if(d.error&&!d.available){
    val.innerHTML=`<span class="dot warn"></span> Cannot check updates <span style="color:var(--text-2);font-size:11px;margin-left:6px">${ver}</span>`;
    actions.innerHTML=`<span style="font-size:12px;color:var(--text-2)">${d.error}</span><button class="sec" onclick="loadUpdateCard()" style="font-size:12px;margin-left:8px">Retry</button>`;
    return;
  }
  if(d.available){
    val.innerHTML=`<span class="dot warn"></span> ${d.commits} commit${d.commits!==1?'s':''} available <span style="color:var(--text-2);font-size:11px;margin-left:6px">${ver}</span>`;
    actions.innerHTML=`<button onclick="applyUpdate()" style="font-size:12px">&#x2B06; Apply Update</button><button class="sec" onclick="loadUpdateCard()" style="font-size:12px;margin-left:4px">Check again</button>`;
  }else{
    val.innerHTML=`<span class="dot ok"></span> Up to date <span style="color:var(--text-2);font-size:11px;margin-left:6px">${ver}</span>`;
    actions.innerHTML=`<button class="sec" onclick="loadUpdateCard()" style="font-size:12px">Check for updates</button>`;
  }
}
async function applyUpdate(){
  const val=document.getElementById('update-val');
  const actions=document.getElementById('update-actions');
  val.innerHTML='<span class="dot"></span> Applying update...';
  actions.innerHTML='';
  const r=await api('/api/update/apply','POST',{});
  if(!r.ok){
    val.innerHTML='<span class="dot err"></span> Update failed';
    actions.innerHTML=`<span style="font-size:12px;color:var(--err)">${r.error}</span>`;
    return;
  }
  if(r.restarting){
    val.innerHTML='<span class="dot"></span> Restarting server...';
    pollReconnect();
  }else{
    val.innerHTML='<span class="dot ok"></span> Updated — restart configure to apply';
    actions.innerHTML=`<button class="sec" onclick="loadUpdateCard()" style="font-size:12px">Refresh</button>`;
  }
}
function pollReconnect(){
  const val=document.getElementById('update-val');
  let attempts=0;
  const iv=setInterval(async function(){
    attempts++;
    try{
      const r=await fetch('/api/status');
      if(r.ok){clearInterval(iv);location.reload();}
    }catch(e){}
    if(attempts>30){
      clearInterval(iv);
      val.innerHTML='<span class="dot warn"></span> Server restarted — <a href="javascript:location.reload()">reload page</a>';
    }
  },1000);
}
```

- [ ] **Step 4: Verify JS syntax**

```
python3 -m unittest tests.test_configure.TestHtmlJs -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add configure.py
git commit -m "feat: dashboard update card with check/apply/reconnect"
```

---

## Task 6: install.sh §5–§7

**Files:**
- Modify: `install.sh` (add sections 5, 6, 7 before the final `echo "=== Done ==="`)

- [ ] **Step 1: Add §5 — Install binary**

Replace the `echo ""` + `echo "=== Done ==="` block at the end of `install.sh` with the full new content:

```bash
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
```

- [ ] **Step 2: Remove the old "Next steps" block**

The old block (lines ~50–62) is now replaced by the new `echo "=== Done ==="` block above. Verify `install.sh` ends cleanly with no duplicate "Done" or "Next steps" output:

```bash
bash -n install.sh && echo "Syntax OK"
```

Expected: `Syntax OK`

- [ ] **Step 3: Manual smoke test — binary install**

```bash
bash install.sh
which configure          # should print ~/.local/bin/configure
configure --help 2>&1 | head -3   # should start server (Ctrl+C to stop)
```

- [ ] **Step 4: Manual smoke test — service (Linux/WSL2)**

```bash
systemctl --user status oculus-configure
# Expected: active (running)
curl -s http://localhost:4827/api/status | python3 -m json.tool | head -5
# Expected: JSON with "items" array
```

- [ ] **Step 5: Manual smoke test — repo_path recorded**

```bash
python3 -c "import json,pathlib; d=json.loads(pathlib.Path('~/.claude/settings.json').expanduser().read_text()); print(d['oculus']['repo_path'])"
# Expected: /path/to/oculus-configs
```

- [ ] **Step 6: Run full test suite to confirm no regressions**

```bash
python3 -m unittest tests.test_configure -v
```

Expected: all tests PASS

- [ ] **Step 7: Commit and push**

```bash
git add install.sh configure.py tests/test_configure.py
git commit -m "feat: install.sh service setup + self-update backend complete"
git push origin main
```

---

## Manual Test Checklist (for fresh machine validation)

Run these after shipping — cannot be automated:

- [ ] Clone repo on a fresh machine: `git clone git@github.com:oculus-pllx/oculus-configs.git && cd oculus-configs`
- [ ] Run install: `bash install.sh` — no errors, `[ok]` for all sections
- [ ] `configure` command available: `which configure` returns `~/.local/bin/configure`
- [ ] Browser opens to `http://localhost:4827`
- [ ] Dashboard shows update card (may show "repo not configured" if install just ran — refresh after ~5s)
- [ ] Re-run `bash install.sh` — service restarts cleanly, no duplicate units
- [ ] Push a test commit to remote → Dashboard update card shows "1 commit available"
- [ ] Click "Apply Update" → page shows "Restarting…" → auto-reloads → back to up-to-date state
