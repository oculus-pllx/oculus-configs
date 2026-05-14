# New Project Wizard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a 4-step in-browser wizard to `configure.py` that creates a project folder, copies templates, runs `git init`, and optionally sets up a GitHub remote — all without leaving the browser.

**Architecture:** New backend Python functions (`which_gh`, `create_project`, `github_project`, `remote_project`, `open_vscode`) wired into the existing `ConfigHandler`. New `<section id="newproject">` added to the embedded HTML string with a progress-bar stepped wizard driven by a `wizardState` JS object. No new files — everything stays in `configure.py`.

**Tech Stack:** Python 3 stdlib (`subprocess`, `shutil`, `re`, `pathlib`), vanilla JS, embedded HTML/CSS in a Python string.

---

## File Map

| File | Change |
|------|--------|
| `configure.py` | Add imports, 5 backend functions, 5 HTTP routes, CSS, nav entry, section HTML, JS functions |
| `tests/test_configure.py` | Add `TestWhichGh`, `TestCreateProject`, `TestProjectGithub` test classes |

---

## Task 1: Add imports + `which_gh()` + test + wire into GET handler

**Files:**
- Modify: `configure.py:1-8` (imports), `configure.py:~240` (new function), `configure.py:~831` (GET handler)
- Test: `tests/test_configure.py`

- [ ] **Step 1: Write the failing test**

Add this class to `tests/test_configure.py`:

```python
class TestWhichGh(unittest.TestCase):
    def test_returns_gh_and_code_keys(self):
        import configure
        result = configure.which_gh()
        self.assertIn("gh", result)
        self.assertIn("code", result)
        self.assertIsInstance(result["gh"], bool)
        self.assertIsInstance(result["code"], bool)

    def test_gh_false_when_not_in_path(self):
        import configure
        with patch("configure.shutil") as mock_shutil:
            mock_shutil.which.return_value = None
            result = configure.which_gh()
        self.assertFalse(result["gh"])
        self.assertFalse(result["code"])
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /home/peyton/repos/oculus-configs
python3 -m pytest tests/test_configure.py::TestWhichGh -v
```

Expected: `FAIL` with `AttributeError: module 'configure' has no attribute 'which_gh'`

- [ ] **Step 3: Add imports at the top of `configure.py`**

Replace the existing imports block (lines 1–8) with:

```python
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
```

- [ ] **Step 4: Add `which_gh()` after the `browse_dir()` function (around line 240)**

```python
def which_gh() -> dict:
    return {
        "gh": shutil.which("gh") is not None,
        "code": shutil.which("code") is not None,
    }
```

- [ ] **Step 5: Wire into `do_GET` in `ConfigHandler`**

In `do_GET`, add after the `elif path == "/api/browse":` block:

```python
        elif path == "/api/which/gh":
            self._send_json(which_gh())
```

- [ ] **Step 6: Run tests to verify they pass**

```bash
python3 -m pytest tests/test_configure.py::TestWhichGh -v
```

Expected: both tests PASS

- [ ] **Step 7: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add which_gh() + GET /api/which/gh endpoint"
```

---

## Task 2: `slugify()`, `_copy_templates()`, `create_project()` + tests + wire POST handler

**Files:**
- Modify: `configure.py` (new functions after `which_gh`, new POST route)
- Test: `tests/test_configure.py`

- [ ] **Step 1: Write the failing tests**

Add this class to `tests/test_configure.py`:

```python
class TestCreateProject(unittest.TestCase):
    def test_create_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            result = configure.create_project("My New Project", tmp, ["CLAUDE.md"])
            self.assertTrue(result["ok"])
            self.assertIn("path", result)
            self.assertIn("git_log", result)
            project_path = Path(result["path"])
            self.assertTrue(project_path.exists())
            self.assertIn("Initial commit", result["git_log"])
            # folder name is slugified
            self.assertEqual(project_path.name, "my-new-project")

    def test_create_no_templates(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            result = configure.create_project("bare", tmp, [])
            self.assertTrue(result["ok"])
            project_path = Path(result["path"])
            # only .git/ should be present
            contents = [p.name for p in project_path.iterdir()]
            self.assertIn(".git", contents)

    def test_create_folder_already_exists(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            # pre-create the target
            (Path(tmp) / "my-project").mkdir()
            result = configure.create_project("my-project", tmp, [])
            self.assertFalse(result["ok"])
            self.assertIn("already exists", result["error"])

    def test_slugify(self):
        import configure
        self.assertEqual(configure.slugify("Hello World!"), "hello-world-")
        self.assertEqual(configure.slugify("my-project"), "my-project")
        self.assertEqual(configure.slugify("ABC 123"), "abc-123")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_configure.py::TestCreateProject -v
```

Expected: all FAIL with `AttributeError: module 'configure' has no attribute 'create_project'`

- [ ] **Step 3: Add `TEMPLATE_FILES` map after existing `STARTER_DIR` constant (around line 13)**

```python
TEMPLATE_FILES = {
    "CLAUDE.md":         STARTER_DIR / "CLAUDE.md",
    "docs/DECISIONS.md": STARTER_DIR / "docs" / "DECISIONS.md",
    ".gitignore":        STARTER_DIR / ".gitignore",
    "mcp.json":          STARTER_DIR / "mcp.json",
}
```

- [ ] **Step 4: Add `slugify()`, `_copy_templates()`, and `create_project()` after `which_gh()`**

```python
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
```

Note: `--allow-empty` is needed for the no-templates case — `git commit` fails if there's nothing staged.

- [ ] **Step 5: Wire into `do_POST` in `ConfigHandler`**

Add after the `elif path == "/api/templates/deploy":` block:

```python
        elif path == "/api/projects/create":
            body = self._read_body()
            self._send_json(create_project(
                body.get("name", ""),
                body.get("parent", ""),
                body.get("templates", [])
            ))
```

- [ ] **Step 6: Run tests**

```bash
python3 -m pytest tests/test_configure.py::TestCreateProject -v
```

Expected: all 4 tests PASS

- [ ] **Step 7: Run the full test suite to check for regressions**

```bash
python3 -m pytest tests/ -v
```

Expected: all existing tests still PASS

- [ ] **Step 8: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add create_project() + POST /api/projects/create"
```

---

## Task 3: `github_project()`, `remote_project()`, `open_vscode()` + test + wire POST handler

**Files:**
- Modify: `configure.py`
- Test: `tests/test_configure.py`

- [ ] **Step 1: Write the failing test**

Add this class to `tests/test_configure.py`:

```python
class TestProjectGithub(unittest.TestCase):
    def test_github_no_gh_in_path(self):
        import configure
        with patch("configure.shutil") as mock_shutil:
            mock_shutil.which.return_value = None
            with tempfile.TemporaryDirectory() as tmp:
                result = configure.github_project(tmp, "test-repo", True)
        self.assertFalse(result["ok"])
        self.assertIn("error", result)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_configure.py::TestProjectGithub -v
```

Expected: FAIL with `AttributeError: module 'configure' has no attribute 'github_project'`

- [ ] **Step 3: Add `github_project()`, `remote_project()`, and `open_vscode()` after `create_project()`**

```python
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
```

- [ ] **Step 4: Wire all three into `do_POST`**

Add after the `elif path == "/api/projects/create":` block:

```python
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
```

- [ ] **Step 5: Run all tests**

```bash
python3 -m pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add github_project, remote_project, open_vscode + POST routes"
```

---

## Task 4: Add wizard CSS to the `<style>` block

**Files:**
- Modify: `configure.py` (HTML string, inside `<style>`)

The `<style>` block ends at line ~360 with `.brand-edit button{...}`. Find the closing `</style>` tag and add the CSS before it.

- [ ] **Step 1: Add wizard CSS to `configure.py`**

In the HTML string, find `.brand-edit button{padding:6px 12px;font-size:12px;width:100%}` and add immediately after it (before the `</style>` tag):

```css
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
```

- [ ] **Step 2: Verify JS syntax still passes**

```bash
node --check configure.py
```

Expected: no output (no errors)

- [ ] **Step 3: Commit**

```bash
git add configure.py
git commit -m "feat: add New Project wizard CSS"
```

---

## Task 5: Nav entry + `<section>` scaffold + wire `nav()` + adapt `confirmBrowse()`

**Files:**
- Modify: `configure.py` (HTML string — nav, section HTML, JS)

- [ ] **Step 1: Add the nav link between Dashboard and CLAUDE.md**

Find this in the HTML string:
```html
  <a onclick="nav('dashboard',this)" class="active">Dashboard</a>
  <a onclick="nav('wizard',this)">CLAUDE.md</a>
```

Replace with:
```html
  <a onclick="nav('dashboard',this)" class="active">Dashboard</a>
  <a onclick="nav('newproject',this)">New Project</a>
  <a onclick="nav('wizard',this)">CLAUDE.md</a>
```

- [ ] **Step 2: Add the section HTML before `</main>`**

Find `</main>` in the HTML string and insert the full section before it:

```html
<section id="newproject">
  <h2>New Project</h2>
  <p class="section-desc">Scaffold a new project — folder, starter files, <code>git init</code>, and optional GitHub remote — without leaving the browser.</p>
  <div class="step-progress">
    <div class="step-dot active" id="np-dot-1">1</div>
    <div class="step-line" id="np-line-1"></div>
    <div class="step-dot" id="np-dot-2">2</div>
    <div class="step-line" id="np-line-2"></div>
    <div class="step-dot" id="np-dot-3">3</div>
    <div class="step-line" id="np-line-3"></div>
    <div class="step-dot" id="np-dot-4">4</div>
  </div>
  <div class="wizard-steps active" id="np-step-1">
    <div class="np-field">
      <label class="field-label">Project Name</label>
      <input type="text" id="np-name" placeholder="my-new-project" oninput="npUpdateSlug();npValidate1()" style="max-width:400px">
      <div class="np-slug" id="np-slug">→ my-new-project/</div>
    </div>
    <div class="np-field">
      <label class="field-label">Parent Folder</label>
      <div style="display:flex;gap:8px;max-width:400px">
        <input type="text" id="np-parent" placeholder="/home/user/projects" style="flex:1" oninput="npValidate1()">
        <button class="sec" onclick="openBrowse(function(p){document.getElementById('np-parent').value=p;npValidate1();})" style="flex-shrink:0;white-space:nowrap">Browse...</button>
      </div>
    </div>
    <div class="step-actions end" style="max-width:400px">
      <button id="np-next-1" onclick="showStep(2)" disabled>Next →</button>
    </div>
  </div>
  <div class="wizard-steps" id="np-step-2">
    <p class="section-desc" style="margin-bottom:16px">Choose which starter files to copy into your new project.</p>
    <label class="np-check-row"><input type="checkbox" id="np-tpl-claude" checked style="width:auto"> CLAUDE.md</label>
    <label class="np-check-row"><input type="checkbox" id="np-tpl-decisions" checked style="width:auto"> docs/DECISIONS.md</label>
    <label class="np-check-row"><input type="checkbox" id="np-tpl-gitignore" checked style="width:auto"> .gitignore</label>
    <label class="np-check-row"><input type="checkbox" id="np-tpl-mcp" style="width:auto"> mcp.json</label>
    <div class="step-actions" style="max-width:400px">
      <button class="sec" onclick="showStep(1)">← Back</button>
      <button onclick="showStep(3)">Next →</button>
    </div>
  </div>
  <div class="wizard-steps" id="np-step-3">
    <p class="section-desc" style="margin-bottom:12px"><code>git init</code> and an "Initial commit" run automatically. Optionally connect a GitHub remote.</p>
    <div class="np-field">
      <label class="field-label">GitHub Remote (optional)</label>
      <div class="np-radio-group" id="np-remote-opts"></div>
      <div id="np-gh-vis-opts" style="display:none;margin-bottom:10px">
        <label class="field-label">Visibility</label>
        <div class="np-radio-group">
          <div class="np-radio active" id="np-vis-private" onclick="npSelectVis('private')">● Private</div>
          <div class="np-radio" id="np-vis-public" onclick="npSelectVis('public')">○ Public</div>
        </div>
      </div>
      <div id="np-url-field" style="display:none;max-width:400px">
        <input type="text" id="np-remote-url" placeholder="git@github.com:user/repo.git">
      </div>
    </div>
    <div id="np-create-err" class="np-err" style="display:none"></div>
    <div class="step-actions" style="max-width:400px">
      <button class="sec" onclick="showStep(2)">← Back</button>
      <button id="np-create-btn" onclick="npCreate()">Create Project</button>
    </div>
  </div>
  <div class="wizard-steps" id="np-step-4">
    <div class="np-ok">✓ Project created!</div>
    <div class="np-result" id="np-path-display"></div>
    <div class="np-result" id="np-log-display" style="color:var(--text-5)"></div>
    <div id="np-clone-section" style="display:none;margin-bottom:16px;max-width:500px">
      <label class="field-label">Clone URL</label>
      <div style="display:flex;gap:8px">
        <input type="text" id="np-clone-url" style="flex:1;font-family:monospace;font-size:12px" readonly>
        <button class="sec" onclick="navigator.clipboard.writeText(document.getElementById('np-clone-url').value).then(()=>toast('Copied!'))" style="flex-shrink:0">Copy</button>
      </div>
    </div>
    <div id="np-git-err" class="np-err" style="display:none"></div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:8px">
      <button id="np-vscode-btn" style="display:none" onclick="npOpenVscode()">⌗ Open in VS Code</button>
      <button class="sec" onclick="npReset()">+ New Project</button>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Wire `loadNewProject()` into the `nav()` function**

Find the `nav()` JS function:
```javascript
  else if(id==='templates')loadTpl('template-claude');
```

Add after it:
```javascript
  else if(id==='newproject')loadNewProject();
```

- [ ] **Step 4: Adapt `confirmBrowse()` and `openBrowse()` to support a callback**

Find in the JS:
```javascript
let browseData={};
function openBrowse(){
  document.getElementById('browse-modal').style.display='flex';
  navigateBrowse('~');
}
```

Replace with:
```javascript
let browseData={};let browseCallback=null;
function openBrowse(cb){
  browseCallback=cb||null;
  document.getElementById('browse-modal').style.display='flex';
  navigateBrowse('~');
}
```

Find:
```javascript
function confirmBrowse(){
  const p=browseData.path||'';
  if(p)document.getElementById('deploy-path').value=p;
  closeBrowse();
}
```

Replace with:
```javascript
function confirmBrowse(){
  const p=browseData.path||'';
  if(browseCallback){browseCallback(p);browseCallback=null;}
  else if(p){document.getElementById('deploy-path').value=p;}
  closeBrowse();
}
```

- [ ] **Step 5: Verify JS syntax**

```bash
node --check configure.py
```

Expected: no output

- [ ] **Step 6: Smoke test — start the server and verify the nav link appears**

```bash
python3 configure.py &
sleep 1
curl -s http://localhost:4827/ | grep -o 'New Project'
kill %1
```

Expected: `New Project`

- [ ] **Step 7: Commit**

```bash
git add configure.py
git commit -m "feat: add New Project section scaffold, nav entry, adapt confirmBrowse()"
```

---

## Task 6: Add all wizard JS functions

**Files:**
- Modify: `configure.py` (JS block inside HTML string)

Add all wizard JS functions inside the `<script>` block, before the closing `</script>` tag. The `</script>` tag immediately precedes `</body></html>` — find `loadBranding();\\nloadDash();` which are the last two lines of script, and add the new functions before them.

- [ ] **Step 1: Add `wizardState`, `showStep()`, and `loadNewProject()` to the script**

```javascript
let wizardState={};

function showStep(n){
  document.querySelectorAll('.wizard-steps').forEach(s=>s.classList.remove('active'));
  document.getElementById('np-step-'+n).classList.add('active');
  for(let i=1;i<=4;i++){
    const dot=document.getElementById('np-dot-'+i);
    const line=i<4?document.getElementById('np-line-'+i):null;
    if(i<n){dot.className='step-dot done';dot.textContent='✓';if(line)line.className='step-line done';}
    else if(i===n){dot.className='step-dot active';dot.textContent=String(i);if(line)line.className='step-line';}
    else{dot.className='step-dot';dot.textContent=String(i);if(line)line.className='step-line';}
  }
}

async function loadNewProject(){
  if(!wizardState.caps){
    wizardState.caps=await api('/api/which/gh');
    wizardState.visibility='private';
    npBuildRemoteOpts();
  }
}
```

- [ ] **Step 2: Add `npBuildRemoteOpts()`, `npSelectRemote()`, `npSelectVis()`**

```javascript
function npBuildRemoteOpts(){
  const opts=document.getElementById('np-remote-opts');
  opts.innerHTML='';
  if(wizardState.caps.gh){
    const ghBtn=document.createElement('div');
    ghBtn.className='np-radio';ghBtn.id='np-opt-gh';ghBtn.textContent='● gh create';
    ghBtn.onclick=()=>npSelectRemote('gh');
    opts.appendChild(ghBtn);
  }
  const urlBtn=document.createElement('div');
  urlBtn.className='np-radio';urlBtn.id='np-opt-url';urlBtn.textContent='○ Manual URL';
  urlBtn.onclick=()=>npSelectRemote('url');
  opts.appendChild(urlBtn);
  const skipBtn=document.createElement('div');
  skipBtn.className='np-radio';skipBtn.id='np-opt-skip';skipBtn.textContent='○ Skip';
  skipBtn.onclick=()=>npSelectRemote('skip');
  opts.appendChild(skipBtn);
  npSelectRemote(wizardState.caps.gh?'gh':'skip');
}

function npSelectRemote(mode){
  wizardState.remoteMode=mode;
  ['gh','url','skip'].forEach(id=>{
    const el=document.getElementById('np-opt-'+id);
    if(el)el.className='np-radio'+(id===mode?' active':'');
  });
  document.getElementById('np-gh-vis-opts').style.display=mode==='gh'?'block':'none';
  document.getElementById('np-url-field').style.display=mode==='url'?'block':'none';
}

function npSelectVis(vis){
  wizardState.visibility=vis;
  document.getElementById('np-vis-private').className='np-radio'+(vis==='private'?' active':'');
  document.getElementById('np-vis-public').className='np-radio'+(vis==='public'?' active':'');
}
```

- [ ] **Step 3: Add `npUpdateSlug()` and `npValidate1()`**

```javascript
function npUpdateSlug(){
  const name=document.getElementById('np-name').value;
  const slug=name.toLowerCase().replace(/[^a-z0-9-]/g,'-');
  wizardState.slug=slug;
  document.getElementById('np-slug').textContent='→ '+(slug||'my-new-project')+'/';
}

function npValidate1(){
  const name=document.getElementById('np-name').value.trim();
  const parent=document.getElementById('np-parent').value.trim();
  document.getElementById('np-next-1').disabled=!(name&&parent);
}
```

- [ ] **Step 4: Add `npCreate()`**

```javascript
async function npCreate(){
  document.getElementById('np-create-err').style.display='none';
  const name=document.getElementById('np-name').value.trim();
  const parent=document.getElementById('np-parent').value.trim();
  const templates=[];
  if(document.getElementById('np-tpl-claude').checked)templates.push('CLAUDE.md');
  if(document.getElementById('np-tpl-decisions').checked)templates.push('docs/DECISIONS.md');
  if(document.getElementById('np-tpl-gitignore').checked)templates.push('.gitignore');
  if(document.getElementById('np-tpl-mcp').checked)templates.push('mcp.json');
  const btn=document.getElementById('np-create-btn');
  btn.disabled=true;btn.textContent='Creating...';
  const result=await api('/api/projects/create','POST',{name,parent,templates});
  if(!result.ok){
    document.getElementById('np-create-err').textContent=result.error;
    document.getElementById('np-create-err').style.display='block';
    btn.disabled=false;btn.textContent='Create Project';
    return;
  }
  wizardState.createdPath=result.path;
  let cloneUrl='';let ghErr='';
  if(wizardState.remoteMode==='gh'){
    const gr=await api('/api/projects/github','POST',{path:result.path,repo_name:wizardState.slug,private:wizardState.visibility!=='public'});
    if(gr.ok)cloneUrl=gr.clone_url;else ghErr=gr.error;
  } else if(wizardState.remoteMode==='url'){
    const ru=document.getElementById('np-remote-url').value.trim();
    if(ru){const rr=await api('/api/projects/remote','POST',{path:result.path,remote_url:ru});if(rr.ok)cloneUrl=rr.clone_url;else ghErr=rr.error;}
  }
  showStep(4);
  document.getElementById('np-path-display').textContent=result.path;
  document.getElementById('np-log-display').textContent=result.git_log;
  if(cloneUrl){document.getElementById('np-clone-url').value=cloneUrl;document.getElementById('np-clone-section').style.display='block';}
  if(ghErr){document.getElementById('np-git-err').textContent='GitHub: '+ghErr;document.getElementById('np-git-err').style.display='block';}
  if(wizardState.caps.code)document.getElementById('np-vscode-btn').style.display='inline-block';
  btn.disabled=false;btn.textContent='Create Project';
}
```

- [ ] **Step 5: Add `npOpenVscode()` and `npReset()`**

```javascript
async function npOpenVscode(){
  await api('/api/projects/open-vscode','POST',{path:wizardState.createdPath});
}

function npReset(){
  wizardState={caps:wizardState.caps,visibility:'private'};
  document.getElementById('np-name').value='';
  document.getElementById('np-slug').textContent='→ my-new-project/';
  document.getElementById('np-parent').value='';
  document.getElementById('np-next-1').disabled=true;
  document.getElementById('np-tpl-claude').checked=true;
  document.getElementById('np-tpl-decisions').checked=true;
  document.getElementById('np-tpl-gitignore').checked=true;
  document.getElementById('np-tpl-mcp').checked=false;
  document.getElementById('np-create-err').style.display='none';
  document.getElementById('np-clone-section').style.display='none';
  document.getElementById('np-git-err').style.display='none';
  document.getElementById('np-vscode-btn').style.display='none';
  npSelectRemote(wizardState.caps.gh?'gh':'skip');
  npSelectVis('private');
  showStep(1);
}
```

- [ ] **Step 6: Verify JS syntax**

```bash
node --check configure.py
```

Expected: no output

- [ ] **Step 7: Run the full test suite**

```bash
python3 -m pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 8: Commit**

```bash
git add configure.py
git commit -m "feat: add New Project wizard JS — complete 4-step flow"
```

---

## Task 7: End-to-end smoke test + final verification

**Files:**
- Modify: none (verification only)

- [ ] **Step 1: Run the full test suite one final time**

```bash
python3 -m pytest tests/ -v
```

Expected: all tests PASS. Note exact count — it should be the previous count plus 6 new tests.

- [ ] **Step 2: Verify JS syntax**

```bash
node --check configure.py
```

Expected: no output

- [ ] **Step 3: Manual smoke test**

```bash
python3 configure.py
```

- Open http://localhost:4827
- Click "New Project" in the nav — verify it's between Dashboard and CLAUDE.md
- Step 1: type a name with spaces (e.g. "Hello World") — verify slug preview updates to `hello-world/`
- Click Browse — verify the existing folder browser modal opens and selecting a folder populates the parent field
- Verify Next is disabled until both name and parent are filled
- Step 2: verify 3 checkboxes checked by default, mcp.json unchecked
- Step 3: verify remote options appear (gh if installed, URL, Skip)
- Click "Create Project" with Skip selected — verify a project is created in the chosen parent
- Step 4: verify path and git log appear, VS Code button appears if `code` is in PATH
- Click "+ New Project" — verify form resets to step 1

- [ ] **Step 4: Commit if any fixes were needed, otherwise tag the work done**

```bash
git add configure.py
git commit -m "fix: wizard smoke test corrections" # only if fixes were needed
```

---

## Self-Review Notes

**Spec coverage check:**
- ✅ Nav placement (position 2, after Dashboard)
- ✅ Step 1: name + slug preview + folder browser reuse
- ✅ Step 2: 4 checkboxes with correct defaults
- ✅ Step 3: gh/URL/skip options, private/public visibility, caps detection
- ✅ Step 4: path, git log, clone URL, VS Code button, reset
- ✅ `GET /api/which/gh`
- ✅ `POST /api/projects/create` (folder exists error, no templates, git init)
- ✅ `POST /api/projects/github` (no-gh error test)
- ✅ `POST /api/projects/remote`
- ✅ `POST /api/projects/open-vscode`
- ✅ Error handling: folder exists, git fail, gh fail (partial success), Next disabled when empty
- ✅ All 5 tests from spec

**Placeholder scan:** None found.

**Type consistency:**
- `wizardState.caps` set in `loadNewProject()`, read in `npCreate()` and `npReset()` ✅
- `wizardState.slug` set in `npUpdateSlug()`, read in `npCreate()` ✅
- `wizardState.remoteMode` set in `npSelectRemote()`, read in `npCreate()` ✅
- `wizardState.visibility` set in `loadNewProject()` and `npSelectVis()`, read in `npCreate()` and `npReset()` ✅
- `wizardState.createdPath` set in `npCreate()`, read in `npOpenVscode()` ✅
