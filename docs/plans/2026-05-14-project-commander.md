# Project Commander Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the New Project tab into "Project Commander" — a two-card hub for creating projects (existing wizard) and managing existing folders (rename, delete, move, new folder) via an upgraded file-manager browse modal.

**Architecture:** All file system ops go through four new Python backend functions (`fs_mkdir`, `fs_rename`, `fs_delete`, `fs_move`) wired as POST endpoints. The browse modal gains dual-mode behavior: picker mode (existing, unchanged) when called with a callback, file manager mode (new) when called without. Project Commander tab wraps the existing wizard in a sub-panel and adds a home screen with two entry cards.

**Tech Stack:** Python 3 stdlib (`shutil`, `pathlib`), vanilla JS, single-file `configure.py` with embedded HTML/CSS/JS. No new dependencies (ADR-001).

---

## File Map

- **Modify:** `configure.py` — all changes are in this one file
  - Python backend: add `PROTECTED_PATHS`, `_is_protected()`, `fs_mkdir()`, `fs_rename()`, `fs_delete()`, `fs_move()` after line ~324 (after `open_vscode`)
  - HTTP handler: add 4 POST routes in `do_POST` after line ~1195 (after `open-vscode` route)
  - HTML `<style>`: add `.fm-toolbar`, `.fm-item-sel` CSS rules before `</style>` (~line 465)
  - HTML modal (~lines 683–697): add toolbar div, error div, id on Select button
  - HTML newproject section (~lines 600–679): rename heading, add `pc-home` cards, wrap wizard in `pc-create-panel`
  - Nav (~line 471): rename "New Project" to "Project Commander"
  - JS browse functions (~lines 938–974): update `openBrowse`, `navigateBrowse`, `confirmBrowse`; add `fmManagerMode`, `fmSelected` state; add `fmUpdateButtons`, `fmClearError`, `fmShowError`, `fmNewFolder`, `fmRename`, `fmDelete`, `fmConfirmDelete`, `fmMove`
  - JS wizard functions: update `loadNewProject`, `npReset`; add `pcShowCreate`
- **Modify:** `tests/test_configure.py` — add `TestFsMkdir`, `TestFsRename`, `TestFsDelete`, `TestFsMove` classes

---

## Task 1: Backend — PROTECTED_PATHS + fs_mkdir

**Files:**
- Modify: `configure.py` (after `TEMPLATE_FILES` block, ~line 38; after `open_vscode`, ~line 324)
- Modify: `tests/test_configure.py` (add `TestFsMkdir` class)

- [ ] **Step 1: Write the failing tests**

Add this class to `tests/test_configure.py` before the `class TestHtmlJs` line:

```python
class TestFsMkdir(unittest.TestCase):
    def test_mkdir_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            result = configure.fs_mkdir(tmp, "new-folder")
            self.assertTrue(result["ok"])
            self.assertTrue(Path(result["path"]).exists())
            self.assertEqual(Path(result["path"]).name, "new-folder")

    def test_mkdir_already_exists(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "existing").mkdir()
            result = configure.fs_mkdir(tmp, "existing")
        self.assertFalse(result["ok"])
        self.assertIn("already exists", result["error"])

    def test_mkdir_empty_name(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            result = configure.fs_mkdir(tmp, "")
        self.assertFalse(result["ok"])
        self.assertIn("empty", result["error"].lower())
```

- [ ] **Step 2: Run to verify tests fail**

```
python3 -m unittest tests.test_configure.TestFsMkdir -v
```

Expected: FAIL with `AttributeError: module 'configure' has no attribute 'fs_mkdir'`

- [ ] **Step 3: Add PROTECTED_PATHS constant and _is_protected helper**

After the `TEMPLATE_FILES` block (~line 38), add:

```python
REPO_ROOT = Path(__file__).resolve().parent
PROTECTED_PATHS = frozenset({Path.home().resolve(), CLAUDE_DIR.resolve(), REPO_ROOT})


def _is_protected(path: Path) -> bool:
    return path.resolve() in PROTECTED_PATHS
```

- [ ] **Step 4: Implement fs_mkdir**

After the `open_vscode` function (~line 324), add:

```python
def fs_mkdir(parent: str, name: str) -> dict:
    name = (name or "").strip()
    if not name:
        return {"ok": False, "error": "Name cannot be empty"}
    try:
        p = Path(parent).expanduser().resolve() / name
        if _is_protected(p.parent):
            return {"ok": False, "error": "Cannot create folder here — protected path"}
        if p.exists():
            return {"ok": False, "error": f"'{name}' already exists"}
        p.mkdir(parents=False)
        return {"ok": True, "path": str(p)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

- [ ] **Step 5: Run tests to verify they pass**

```
python3 -m unittest tests.test_configure.TestFsMkdir -v
```

Expected: 3 tests PASS

- [ ] **Step 6: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add PROTECTED_PATHS + fs_mkdir backend"
```

---

## Task 2: Backend — fs_rename

**Files:**
- Modify: `configure.py` (add `fs_rename` after `fs_mkdir`)
- Modify: `tests/test_configure.py` (add `TestFsRename`)

- [ ] **Step 1: Write the failing tests**

Add after `TestFsMkdir`:

```python
class TestFsRename(unittest.TestCase):
    def test_rename_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "old-name"
            src.mkdir()
            result = configure.fs_rename(str(src), "new-name")
            self.assertTrue(result["ok"])
            self.assertTrue(Path(tmp, "new-name").exists())
            self.assertFalse(src.exists())

    def test_rename_conflict(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "old").mkdir()
            (Path(tmp) / "taken").mkdir()
            result = configure.fs_rename(str(Path(tmp) / "old"), "taken")
        self.assertFalse(result["ok"])
        self.assertIn("already exists", result["error"])

    def test_rename_empty_name(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "folder"
            src.mkdir()
            result = configure.fs_rename(str(src), "")
        self.assertFalse(result["ok"])
        self.assertIn("empty", result["error"].lower())
```

- [ ] **Step 2: Run to verify tests fail**

```
python3 -m unittest tests.test_configure.TestFsRename -v
```

Expected: FAIL with `AttributeError: module 'configure' has no attribute 'fs_rename'`

- [ ] **Step 3: Implement fs_rename**

Add after `fs_mkdir`:

```python
def fs_rename(path: str, new_name: str) -> dict:
    new_name = (new_name or "").strip()
    if not new_name:
        return {"ok": False, "error": "Name cannot be empty"}
    try:
        src = Path(path).expanduser().resolve()
        if _is_protected(src):
            return {"ok": False, "error": "Cannot rename — protected path"}
        dest = src.parent / new_name
        if dest.exists():
            return {"ok": False, "error": f"'{new_name}' already exists"}
        src.rename(dest)
        return {"ok": True, "path": str(dest)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

- [ ] **Step 4: Run tests to verify they pass**

```
python3 -m unittest tests.test_configure.TestFsRename -v
```

Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add fs_rename backend"
```

---

## Task 3: Backend — fs_delete

**Files:**
- Modify: `configure.py` (add `fs_delete` after `fs_rename`)
- Modify: `tests/test_configure.py` (add `TestFsDelete`)

- [ ] **Step 1: Write the failing tests**

Add after `TestFsRename`:

```python
class TestFsDelete(unittest.TestCase):
    def test_delete_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "to-delete"
            target.mkdir()
            (target / "child.txt").write_text("hi")
            result = configure.fs_delete(str(target))
        self.assertTrue(result["ok"])
        self.assertFalse(target.exists())

    def test_delete_not_found(self):
        import configure
        result = configure.fs_delete("/nonexistent/path/that/does/not/exist")
        self.assertFalse(result["ok"])
        self.assertIn("not found", result["error"].lower())

    def test_delete_protected(self):
        import configure
        result = configure.fs_delete(str(Path.home()))
        self.assertFalse(result["ok"])
        self.assertIn("protected", result["error"].lower())
```

- [ ] **Step 2: Run to verify tests fail**

```
python3 -m unittest tests.test_configure.TestFsDelete -v
```

Expected: FAIL with `AttributeError: module 'configure' has no attribute 'fs_delete'`

- [ ] **Step 3: Implement fs_delete**

Add after `fs_rename`:

```python
def fs_delete(path: str) -> dict:
    try:
        p = Path(path).expanduser().resolve()
        if _is_protected(p):
            return {"ok": False, "error": "Cannot delete — protected path"}
        if not p.exists():
            return {"ok": False, "error": "Path not found"}
        shutil.rmtree(p)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

- [ ] **Step 4: Run tests to verify they pass**

```
python3 -m unittest tests.test_configure.TestFsDelete -v
```

Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add fs_delete backend"
```

---

## Task 4: Backend — fs_move + wire all four endpoints

**Files:**
- Modify: `configure.py` (add `fs_move`; add 4 POST routes in `do_POST`)
- Modify: `tests/test_configure.py` (add `TestFsMove`)

- [ ] **Step 1: Write the failing tests**

Add after `TestFsDelete`:

```python
class TestFsMove(unittest.TestCase):
    def test_move_success(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "src-folder"
            dest = Path(tmp) / "dest-parent"
            src.mkdir(); dest.mkdir()
            result = configure.fs_move(str(src), str(dest))
            self.assertTrue(result["ok"])
            self.assertTrue(Path(tmp, "dest-parent", "src-folder").exists())
            self.assertFalse(src.exists())

    def test_move_name_conflict(self):
        import configure
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "my-folder"
            dest = Path(tmp) / "dest"
            conflict = dest / "my-folder"
            src.mkdir(); dest.mkdir(); conflict.mkdir()
            result = configure.fs_move(str(src), str(dest))
        self.assertFalse(result["ok"])
        self.assertIn("already exists", result["error"])
```

- [ ] **Step 2: Run to verify tests fail**

```
python3 -m unittest tests.test_configure.TestFsMove -v
```

Expected: FAIL with `AttributeError: module 'configure' has no attribute 'fs_move'`

- [ ] **Step 3: Implement fs_move**

Add after `fs_delete`:

```python
def fs_move(src: str, dest_parent: str) -> dict:
    try:
        s = Path(src).expanduser().resolve()
        d = Path(dest_parent).expanduser().resolve()
        if _is_protected(s):
            return {"ok": False, "error": "Cannot move — protected path"}
        if s == d:
            return {"ok": False, "error": "Source and destination are the same"}
        target = d / s.name
        if target.exists():
            return {"ok": False, "error": f"'{s.name}' already exists in destination"}
        shutil.move(str(s), str(target))
        return {"ok": True, "path": str(target)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
```

- [ ] **Step 4: Run tests to verify they pass**

```
python3 -m unittest tests.test_configure.TestFsMove -v
```

Expected: 2 tests PASS

- [ ] **Step 5: Wire all four POST endpoints in do_POST**

In `do_POST`, after the `elif path == "/api/projects/open-vscode":` block and before the final `else:`, add:

```python
        elif path == "/api/fs/mkdir":
            body = self._read_body()
            self._send_json(fs_mkdir(body.get("parent", ""), body.get("name", "")))
        elif path == "/api/fs/rename":
            body = self._read_body()
            self._send_json(fs_rename(body.get("path", ""), body.get("new_name", "")))
        elif path == "/api/fs/delete":
            body = self._read_body()
            self._send_json(fs_delete(body.get("path", "")))
        elif path == "/api/fs/move":
            body = self._read_body()
            self._send_json(fs_move(body.get("src", ""), body.get("dest", "")))
```

- [ ] **Step 6: Run full test suite**

```
python3 -m unittest tests.test_configure -v
```

Expected: all tests PASS (should now be ~35 tests)

- [ ] **Step 7: Commit**

```bash
git add configure.py tests/test_configure.py
git commit -m "feat: add fs_move backend + wire all four /api/fs/* endpoints"
```

---

## Task 5: Browse modal — HTML + CSS for manager mode

**Files:**
- Modify: `configure.py` (CSS block ~line 460–465; modal HTML ~lines 683–697)

The browse modal needs: a toolbar div (hidden by default), an error message div, and an `id` on the Select button so JS can toggle it. CSS needs rules for the toolbar and selected-item highlight.

- [ ] **Step 1: Add CSS rules**

In the `<style>` block, just before `</style>` (~line 465), add:

```css
    .fm-toolbar{display:none;padding:6px 12px;border-bottom:1px solid var(--border);gap:6px;flex-wrap:wrap}
    .fm-toolbar.active{display:flex}
    .fm-toolbar .sec{font-size:12px;padding:4px 10px}
    .fm-item-sel{background:var(--accent)!important;color:#fff!important}
    .fm-error{display:none;padding:4px 14px 6px;font-size:12px;color:var(--err)}
```

- [ ] **Step 2: Update the browse modal HTML**

Replace the entire modal block (lines 683–697):

```html
<div class="modal-overlay" id="browse-modal" style="display:none" onclick="if(event.target===this)closeBrowse()">
  <div class="modal">
    <div class="modal-header">
      <h3 id="browse-title">Select Project Folder</h3>
      <button onclick="closeBrowse()">&#x2715;</button>
    </div>
    <div class="modal-crumb" id="browse-crumb">/</div>
    <div id="fm-toolbar" class="fm-toolbar">
      <button class="sec" onclick="fmNewFolder()">+ New Folder</button>
      <button class="sec" id="fm-rename-btn" onclick="fmRename()" disabled>Rename</button>
      <button class="sec" id="fm-delete-btn" onclick="fmDelete()" style="color:var(--err)" disabled>Delete</button>
      <button class="sec" id="fm-move-btn" onclick="fmMove()" disabled>Move</button>
    </div>
    <div class="fm-error" id="fm-error"></div>
    <div class="modal-list" id="browse-list"></div>
    <div class="modal-footer">
      <span class="sel-path" id="browse-sel"></span>
      <button class="sec" onclick="closeBrowse()">Cancel</button>
      <button id="browse-select-btn" onclick="confirmBrowse()">Select This Folder</button>
    </div>
  </div>
</div>
```

- [ ] **Step 3: Verify JS syntax still passes**

```
python3 -m unittest tests.test_configure.TestHtmlJs -v
```

Expected: PASS (HTML changes don't affect JS syntax check)

- [ ] **Step 4: Commit**

```bash
git add configure.py
git commit -m "feat: browse modal HTML+CSS for file manager mode (toolbar, error div, ids)"
```

---

## Task 6: Browse modal — JS dual-mode behavior

**Files:**
- Modify: `configure.py` (JS section ~lines 938–974; add fm* functions before `let wizardState`)

This is the largest JS change. We add two state variables (`fmManagerMode`, `fmSelected`), rewrite `openBrowse` and `navigateBrowse` to branch on mode, update `confirmBrowse` to not close when in manager move-picking mode, and add all the fm* action functions.

- [ ] **Step 1: Replace the browse state + openBrowse + closeBrowse + confirmBrowse + navigateBrowse block**

Find and replace the block from `let browseData={}` through the end of `navigateBrowse` (lines ~938–974) with:

```javascript
let browseData={};let browseCallback=null;
let fmManagerMode=false;let fmSelected=null;

function openBrowse(cb){
  browseCallback=cb||null;
  fmManagerMode=!cb;
  fmSelected=null;
  document.getElementById('browse-title').textContent=fmManagerMode?'File Manager':'Select Project Folder';
  document.getElementById('fm-toolbar').classList.toggle('active',fmManagerMode);
  document.getElementById('browse-select-btn').style.display=fmManagerMode?'none':'';
  document.getElementById('browse-select-btn').textContent='Select This Folder';
  fmClearError();
  fmUpdateButtons();
  document.getElementById('browse-modal').style.display='flex';
  navigateBrowse('~');
}
function closeBrowse(){
  document.getElementById('browse-modal').style.display='none';
  browseCallback=null;
  fmManagerMode=false;
  fmSelected=null;
}
function confirmBrowse(){
  const p=browseData.path||'';
  if(browseCallback){
    const cb=browseCallback;browseCallback=null;cb(p);
    if(!fmManagerMode)closeBrowse();
  }else if(p){document.getElementById('deploy-path').value=p;closeBrowse();}
}
async function navigateBrowse(path){
  const d=await api('/api/browse?path='+encodeURIComponent(path));
  browseData=d;
  fmSelected=null;
  fmUpdateButtons();
  fmClearError();
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
    if(fmManagerMode&&!el.classList.contains('up')){
      el.addEventListener('click',function(){
        list.querySelectorAll('.modal-item').forEach(function(x){x.classList.remove('fm-item-sel');});
        el.classList.add('fm-item-sel');
        fmSelected=el.dataset.path;
        document.getElementById('browse-sel').textContent=fmSelected;
        fmUpdateButtons();
      });
      el.addEventListener('dblclick',function(){navigateBrowse(el.dataset.path);});
    }else{
      el.addEventListener('click',function(){navigateBrowse(this.dataset.path);});
    }
  });
}
```

- [ ] **Step 2: Add fm* helper and action functions**

Immediately after the `navigateBrowse` function and before `let wizardState={}`, add:

```javascript
function fmUpdateButtons(){
  const has=!!fmSelected;
  ['fm-rename-btn','fm-delete-btn','fm-move-btn'].forEach(function(id){
    document.getElementById(id).disabled=!has;
  });
}
function fmClearError(){
  const el=document.getElementById('fm-error');el.style.display='none';el.innerHTML='';
}
function fmShowError(msg){
  const el=document.getElementById('fm-error');el.textContent=msg;el.style.display='block';
}
function fmNewFolder(){
  fmClearError();
  const list=document.getElementById('browse-list');
  const old=list.querySelector('.fm-inline');if(old)old.remove();
  const row=document.createElement('div');
  row.className='modal-item fm-inline';
  row.innerHTML='<span class="icon">&#x1F4C1;</span><input type="text" placeholder="folder-name" style="flex:1;background:transparent;border:none;border-bottom:1px solid var(--accent);color:var(--text);outline:none;font-size:13px">';
  list.insertBefore(row,list.firstChild);
  const inp=row.querySelector('input');inp.focus();
  inp.addEventListener('keydown',async function(e){
    if(e.key==='Enter'){
      const r=await api('/api/fs/mkdir','POST',{parent:browseData.path,name:inp.value});
      if(r.ok)navigateBrowse(browseData.path);else fmShowError(r.error);
    }else if(e.key==='Escape'){row.remove();}
  });
}
async function fmRename(){
  if(!fmSelected)return;fmClearError();
  const list=document.getElementById('browse-list');
  const el=list.querySelector('[data-path="'+fmSelected+'"]');
  if(!el)return;
  const oldName=fmSelected.split('/').pop();
  el.innerHTML='<span class="icon">&#x1F4C1;</span><input type="text" value="'+oldName+'" style="flex:1;background:transparent;border:none;border-bottom:1px solid var(--accent);color:var(--text);outline:none;font-size:13px">';
  const inp=el.querySelector('input');inp.focus();inp.select();
  inp.addEventListener('keydown',async function(e){
    if(e.key==='Enter'){
      const r=await api('/api/fs/rename','POST',{path:fmSelected,new_name:inp.value.trim()});
      if(r.ok){fmSelected=null;navigateBrowse(browseData.path);}else fmShowError(r.error);
    }else if(e.key==='Escape'){navigateBrowse(browseData.path);}
  });
}
function fmDelete(){
  if(!fmSelected)return;fmClearError();
  const name=fmSelected.split('/').pop();
  const el=document.getElementById('fm-error');el.style.display='block';
  el.innerHTML='Delete <strong>'+name+'</strong> and all contents? Type <code>delete</code> to confirm: '
    +'<input id="fm-del-inp" style="width:72px;margin:0 6px;padding:2px 4px;font-size:12px;background:var(--surface);border:1px solid var(--border);color:var(--text);border-radius:3px">'
    +'<button style="font-size:12px;padding:2px 8px;margin-left:2px" onclick="fmConfirmDelete()">OK</button>'
    +'<button class="sec" style="font-size:12px;padding:2px 8px;margin-left:4px" onclick="fmClearError()">Cancel</button>';
  document.getElementById('fm-del-inp').focus();
}
async function fmConfirmDelete(){
  const inp=document.getElementById('fm-del-inp');
  if(!inp||inp.value!=='delete'){fmShowError('Type "delete" to confirm');return;}
  const r=await api('/api/fs/delete','POST',{path:fmSelected});
  if(r.ok){fmSelected=null;navigateBrowse(browseData.path);}else fmShowError(r.error);
}
function fmMove(){
  if(!fmSelected)return;fmClearError();
  const src=fmSelected;
  const srcName=src.split('/').pop();
  // Switch modal to pick-destination sub-mode (browseCallback set; fmManagerMode false)
  fmManagerMode=false;
  document.getElementById('browse-title').textContent='Move “'+srcName+'” — select destination';
  document.getElementById('fm-toolbar').classList.remove('active');
  document.getElementById('browse-select-btn').style.display='';
  document.getElementById('browse-select-btn').textContent='Move Here';
  browseCallback=function(dest){
    // Restore manager mode synchronously before confirmBrowse checks fmManagerMode
    fmManagerMode=true;fmSelected=null;
    document.getElementById('browse-title').textContent='File Manager';
    document.getElementById('fm-toolbar').classList.add('active');
    document.getElementById('browse-select-btn').style.display='none';
    document.getElementById('browse-select-btn').textContent='Select This Folder';
    fmUpdateButtons();
    api('/api/fs/move','POST',{src,dest}).then(function(r){
      navigateBrowse(browseData.path);
      if(!r.ok)fmShowError(r.error);
    });
  };
}
```

- [ ] **Step 3: Verify JS syntax passes**

```
python3 -m unittest tests.test_configure.TestHtmlJs -v
```

Expected: PASS

- [ ] **Step 4: Smoke test in browser**

Start server: `python3 configure.py`  
Navigate to `http://localhost:4827`, go to New Project, click "Browse..." for Parent Folder — picker mode should work exactly as before (single-click navigates, "Select This Folder" button visible, no toolbar).

- [ ] **Step 5: Commit**

```bash
git add configure.py
git commit -m "feat: browse modal dual-mode JS (file manager + all fm* actions)"
```

---

## Task 7: Project Commander tab

**Files:**
- Modify: `configure.py` (nav ~line 471; newproject section ~lines 600–679; loadNewProject + npReset JS)

Rename "New Project" to "Project Commander" throughout, add a home screen with two entry cards, wrap the existing wizard in a sub-panel, and update the two JS functions that control the tab.

- [ ] **Step 1: Update the nav entry**

Change line 471 from:
```html
  <a onclick="nav('newproject',this)">New Project</a>
```
to:
```html
  <a onclick="nav('newproject',this)">Project Commander</a>
```

- [ ] **Step 2: Rewrite the newproject section**

Replace the entire `<section id="newproject">` block (lines 600–679) with:

```html
<section id="newproject">
  <h2>Project Commander</h2>
  <p class="section-desc">Create new projects or manage existing folders — rename, delete, move, and create directories anywhere on your machine.</p>
  <div id="pc-home" style="display:flex;gap:16px;margin-top:16px;flex-wrap:wrap">
    <div class="card" style="flex:1;min-width:200px;cursor:pointer" onclick="pcShowCreate()">
      <div class="val" style="font-size:28px">&#x2795;</div>
      <div class="label">Create New Project</div>
      <p style="font-size:12px;color:var(--text-2);margin:8px 0 0">Scaffold a folder with starter files, git&nbsp;init, and optional GitHub remote</p>
    </div>
    <div class="card" style="flex:1;min-width:200px;cursor:pointer" onclick="openBrowse()">
      <div class="val" style="font-size:28px">&#x1F5C2;&#xFE0F;</div>
      <div class="label">Manage Existing</div>
      <p style="font-size:12px;color:var(--text-2);margin:8px 0 0">Rename, delete, move, or create folders in any directory</p>
    </div>
  </div>
  <div id="pc-create-panel" style="display:none">
    <button class="sec" onclick="loadNewProject()" style="margin:12px 0;font-size:12px">&#x2190; Back to Project Commander</button>
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
        <div class="np-slug" id="np-slug">&#x2192; my-new-project/</div>
      </div>
      <div class="np-field">
        <label class="field-label">Parent Folder</label>
        <div style="display:flex;gap:8px;max-width:400px">
          <input type="text" id="np-parent" placeholder="/home/user/projects" style="flex:1" oninput="npValidate1()">
          <button class="sec" onclick="openBrowse(function(p){document.getElementById('np-parent').value=p;npValidate1();})" style="flex-shrink:0;white-space:nowrap">Browse...</button>
        </div>
      </div>
      <div class="step-actions end" style="max-width:400px">
        <button id="np-next-1" onclick="showStep(2)" disabled>Next &#x2192;</button>
      </div>
    </div>
    <div class="wizard-steps" id="np-step-2">
      <p class="section-desc" style="margin-bottom:16px">Choose which starter files to copy into your new project.</p>
      <label class="np-check-row"><input type="checkbox" id="np-tpl-claude" checked style="width:auto"> CLAUDE.md</label>
      <label class="np-check-row"><input type="checkbox" id="np-tpl-decisions" checked style="width:auto"> docs/DECISIONS.md</label>
      <label class="np-check-row"><input type="checkbox" id="np-tpl-gitignore" checked style="width:auto"> .gitignore</label>
      <label class="np-check-row"><input type="checkbox" id="np-tpl-mcp" style="width:auto"> mcp.json</label>
      <div class="step-actions" style="max-width:400px">
        <button class="sec" onclick="showStep(1)">&#x2190; Back</button>
        <button onclick="showStep(3)">Next &#x2192;</button>
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
            <div class="np-radio active" id="np-vis-private" onclick="npSelectVis('private')">&#x25CF; Private</div>
            <div class="np-radio" id="np-vis-public" onclick="npSelectVis('public')">&#x25CB; Public</div>
          </div>
        </div>
        <div id="np-url-field" style="display:none;max-width:400px">
          <input type="text" id="np-remote-url" placeholder="git@github.com:user/repo.git">
        </div>
      </div>
      <div id="np-create-err" class="np-err" style="display:none"></div>
      <div class="step-actions" style="max-width:400px">
        <button class="sec" onclick="showStep(2)">&#x2190; Back</button>
        <button id="np-create-btn" onclick="npCreate()">Create Project</button>
      </div>
    </div>
    <div class="wizard-steps" id="np-step-4">
      <div class="np-ok">&#x2713; Project created!</div>
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
        <button id="np-vscode-btn" style="display:none" onclick="npOpenVscode()">&#x2317; Open in VS Code</button>
        <button class="sec" onclick="loadNewProject()">&#x2190; Project Commander</button>
      </div>
    </div>
  </div>
</section>
```

- [ ] **Step 3: Update loadNewProject() and add pcShowCreate()**

Replace the existing `loadNewProject` function and add `pcShowCreate`:

```javascript
async function loadNewProject(){
  document.getElementById('pc-home').style.display='flex';
  document.getElementById('pc-create-panel').style.display='none';
  if(!wizardState.caps){
    wizardState.caps=await api('/api/which/gh');
    wizardState.visibility='private';
    npBuildRemoteOpts();
  }
}
function pcShowCreate(){
  document.getElementById('pc-home').style.display='none';
  document.getElementById('pc-create-panel').style.display='block';
  npReset(); // resets fields and calls showStep(1) — panel must be visible first
}
```

- [ ] **Step 4: Update npReset() to reset fields only (not navigate)**

Replace the existing `npReset` function. Note: `npReset` now only resets form state and calls `showStep(1)` — it does NOT navigate to home. Home navigation is handled by `loadNewProject()` (called from the success screen button and the back button). `pcShowCreate()` shows the panel then calls `npReset()`.

```javascript
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

- [ ] **Step 5: Run full test suite**

```
python3 -m unittest tests.test_configure -v
```

Expected: all tests PASS

- [ ] **Step 6: Smoke test in browser**

Kill any running server (`fuser -k 4827/tcp`), then start fresh: `python3 configure.py`

Verify:
- Nav shows "Project Commander" instead of "New Project"
- Clicking "Project Commander" shows two cards
- "Create New Project" card → wizard launches at step 1
- "← Back to Project Commander" button returns to cards
- "Manage Existing" card → file manager modal opens (File Manager title, toolbar visible, no "Select" button)
- In file manager: click a folder to select (highlight), double-click to navigate
- "New Folder" → inline input appears, Enter creates folder, Esc cancels
- "Rename" → inline input with current name, Enter renames
- "Delete" → confirmation input appears, must type `delete` to confirm
- "Move" → modal title changes to "Move... — select destination", toolbar hides, "Move Here" button appears; after selection, manager mode restores
- Picker mode still works: Templates tab "Browse..." opens picker (single-click navigates, no toolbar)

- [ ] **Step 7: Commit**

```bash
git add configure.py
git commit -m "feat: Project Commander tab with entry cards and file manager modal"
```

---

## Final: Push

- [ ] **Push to remote**

```bash
git push origin main
```

- [ ] **Update HANDOFF.md** with new state and next items (HANDOFF.md is gitignored — local only)
