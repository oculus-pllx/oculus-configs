# GUI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the HTML/CSS/JS constant in `configure.py` with a Glass/Aurora aesthetic — top navigation bar, frosted glass surfaces, 3-theme picker (True Aurora, Sky Cyan, Violet), and glowing status indicators.

**Architecture:** All changes are confined to the `HTML` string in `configure.py` (lines 522–1501). The Python API layer, HTTP handler, and all JS application logic (loadDash, loadPlugins, npCreate, etc.) are untouched. The theme system is a `THEMES` JS object whose keys map directly to `docs/themes.md`.

**Tech Stack:** Python stdlib HTTP server, vanilla HTML/CSS/JS embedded as a string constant. No build step. No external dependencies.

---

## File Map

| File | Change |
|------|--------|
| `configure.py:529–645` | Replace `<style>` block entirely |
| `configure.py:647–668` | Replace `<nav>` + remove nav-footer elements |
| `configure.py:670–879` | Wrap each `<section>`'s `<h2>` + desc in `.section-header` div |
| `configure.py:912–916` | Remove `toggleTheme()` function |
| `configure.py:946–957` | Update `nav()` — fix selector `'nav a'` → `'.nav-tab'` |
| `configure.py:1496` | Replace init IIFE (theme restore) |

No new files. No Python changes outside the `HTML` string.

---

## Task 1: Baseline — run tests before touching anything

**Files:** `tests/test_configure.py` (read only)

- [ ] **Step 1: Run the test suite**

```bash
python3 -m pytest tests/test_configure.py -v --tb=short 2>&1 | tail -20
```

Expected: all 65 tests pass. If any fail, stop — do not proceed until the baseline is green.

- [ ] **Step 2: Note the test count**

```bash
python3 -m pytest tests/test_configure.py -q 2>&1 | tail -5
```

Record the pass count. Every task ends by verifying this count hasn't changed.

---

## Task 2: Replace the `<style>` block

**Files:** `configure.py:529–645`

The current style block runs from `<style>` to `</style>` and is replaced entirely. No Python logic changes.

- [ ] **Step 1: Locate the style block boundaries**

```bash
grep -n "<style>\|</style>" configure.py
```

Expected output shows two lines — the opening `<style>` and closing `</style>`.

- [ ] **Step 2: Replace the style block**

In `configure.py`, find the old `<style>` block (starting with `*{box-sizing:border-box...`) and replace everything from `<style>` through `</style>` with:

```css
  <style>
    *{box-sizing:border-box;margin:0;padding:0}

    /* ── Base tokens (theme-neutral) ── */
    :root{
      --bg:#080c12;
      --surface:rgba(255,255,255,.04);
      --surface-hover:rgba(255,255,255,.07);
      --surface-deep:rgba(0,0,0,.25);
      --border:rgba(255,255,255,.08);
      --border-sub:rgba(255,255,255,.05);
      --text:rgba(255,255,255,.82);
      --text-2:rgba(255,255,255,.6);
      --text-3:rgba(255,255,255,.38);
      --text-strong:#fff;
      --ok:#4ade80;--ok-glow:rgba(74,222,128,.4);
      --warn:#fbbf24;--warn-glow:rgba(251,191,36,.3);
      --err:#f87171;--err-glow:rgba(248,113,113,.3);
      --blur:blur(12px);
      --shadow:0 8px 32px rgba(0,0,0,.5);
      /* accent — overridden per theme */
      --accent:#38bdf8;
      --accent-dim:rgba(56,189,248,.12);
      --accent-border:rgba(56,189,248,.25);
      --accent-glow:rgba(56,189,248,.18);
      --wordmark-from:#38bdf8;
      --wordmark-to:#a78bfa;
      /* aurora glows — overridden per theme */
      --glow-a:rgba(56,189,248,.18);
      --glow-b:rgba(139,92,246,.12);
      --glow-c:rgba(16,185,129,.07);
      --glow-d:rgba(56,189,248,.06);
    }

    html,body{height:100%}
    body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);display:flex;flex-direction:column;overflow:hidden;position:relative}

    /* ── Aurora background pseudo-element ── */
    body::before{
      content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
      background:
        radial-gradient(ellipse 60% 40% at 80% 10%,var(--glow-a) 0%,transparent 60%),
        radial-gradient(ellipse 40% 30% at 20% 80%,var(--glow-b) 0%,transparent 55%),
        radial-gradient(ellipse 50% 35% at 50% 50%,var(--glow-c) 0%,transparent 65%),
        radial-gradient(ellipse 30% 25% at 10% 20%,var(--glow-d) 0%,transparent 50%);
      transition:background .5s ease;
    }

    /* ── Top nav ── */
    nav{
      position:relative;z-index:10;
      background:rgba(8,12,18,.6);border-bottom:1px solid var(--border);
      backdrop-filter:var(--blur);-webkit-backdrop-filter:var(--blur);
      padding:0 24px;height:52px;display:flex;align-items:center;gap:0;flex-shrink:0;
    }
    .wordmark{
      font-size:13px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;
      background:linear-gradient(90deg,var(--wordmark-from),var(--wordmark-to));
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
      margin-right:28px;white-space:nowrap;flex-shrink:0;transition:background .5s;
      cursor:default;
    }
    .nav-tabs{display:flex;align-items:stretch;gap:2px;flex:1}
    .nav-tab{
      display:flex;align-items:center;padding:0 14px;height:52px;
      font-size:13px;color:var(--text-3);cursor:pointer;
      border:none;background:none;font-family:inherit;white-space:nowrap;
      transition:color .15s;border-bottom:2px solid transparent;margin-bottom:-1px;
    }
    .nav-tab:hover{color:var(--text)}
    .nav-tab.active{color:var(--accent);border-bottom-color:var(--accent)}
    .nav-right{display:flex;align-items:center;gap:8px;margin-left:auto;padding-left:16px}
    .theme-picker{display:flex;align-items:center;gap:6px}
    .theme-swatch{width:18px;height:18px;border-radius:50%;cursor:pointer;border:2px solid transparent;transition:all .2s}
    .theme-swatch.active{border-color:rgba(255,255,255,.5);transform:scale(1.2)}
    .theme-swatch:hover{transform:scale(1.15)}
    .icon-btn{background:var(--surface);border:1px solid var(--border);color:var(--text-3);padding:5px 8px;font-size:13px;border-radius:6px;cursor:pointer;backdrop-filter:var(--blur);transition:all .15s;font-family:inherit}
    .icon-btn:hover{background:var(--surface-hover);color:var(--text)}

    /* ── Brand edit panel (below nav) ── */
    .brand-edit{
      display:none;position:relative;z-index:9;
      background:rgba(8,12,18,.8);border-bottom:1px solid var(--border);
      backdrop-filter:var(--blur);padding:10px 24px;
      display:none;flex-wrap:wrap;align-items:center;gap:8px;
    }
    .brand-edit input{background:var(--surface-deep);border:1px solid var(--border);border-radius:6px;color:var(--text);padding:6px 10px;font-size:12px;font-family:inherit;outline:none;width:200px}
    .brand-edit input:focus{border-color:var(--accent-border)}
    .brand-edit button{padding:6px 14px;font-size:12px;border-radius:6px;cursor:pointer;font-family:inherit;border:1px solid var(--accent-border);background:var(--accent-dim);color:var(--accent)}
    .brand-edit button.sec{background:var(--surface);border-color:var(--border);color:var(--text-2)}

    /* ── Main content area ── */
    main{flex:1;overflow-y:auto;padding:32px 36px;position:relative;z-index:1}
    section{display:none}
    section.active{display:block}

    /* ── Section headers ── */
    .section-header{margin-bottom:24px}
    h2{font-size:22px;font-weight:700;color:var(--text-strong);display:flex;align-items:center;gap:10px;margin-bottom:6px}
    h3{font-size:14px;font-weight:600;color:var(--text-2);margin-top:20px;margin-bottom:10px}
    .section-desc{font-size:13px;color:var(--text-3);line-height:1.6;max-width:680px}
    .section-desc strong{color:var(--text-2)}
    .scope-badge{font-size:10px;font-weight:500;padding:2px 8px;border-radius:20px;background:var(--accent-dim);color:var(--accent);border:1px solid var(--accent-border);letter-spacing:.3px;text-transform:uppercase}
    .scope-badge.project{background:rgba(74,222,128,.1);color:var(--ok);border-color:rgba(74,222,128,.25)}

    /* ── Cards ── */
    .status-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px;margin-bottom:20px}
    .card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;backdrop-filter:var(--blur);transition:border-color .2s,box-shadow .2s}
    .card:hover{border-color:rgba(255,255,255,.12);box-shadow:var(--shadow)}
    .card.warn{border-color:rgba(251,191,36,.25);background:rgba(251,191,36,.04)}
    .card.err{border-color:rgba(248,113,113,.25);background:rgba(248,113,113,.04)}
    .card .lbl{font-size:11px;color:var(--text-3);font-family:monospace;margin-bottom:4px;letter-spacing:.3px}
    .card .card-desc{font-size:11px;color:var(--text-3);margin-bottom:10px;line-height:1.4}
    .card .val{font-size:13px;color:var(--text);display:flex;align-items:center;gap:8px}
    .card .fix{font-size:11px;color:var(--warn);margin-top:10px;padding-top:10px;border-top:1px solid var(--border);line-height:1.4}
    .card .fix::before{content:"→ "}

    /* ── Status dots ── */
    .dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
    .dot.ok{background:var(--ok);box-shadow:0 0 8px var(--ok-glow)}
    .dot.warn{background:var(--warn);box-shadow:0 0 8px var(--warn-glow)}
    .dot.err{background:var(--err);box-shadow:0 0 8px var(--err-glow)}

    /* ── Forms ── */
    .form-group{margin-bottom:22px}
    .field-label{font-size:12px;color:var(--text-3);margin-bottom:6px;display:block;letter-spacing:.2px}
    .field-help{font-size:11px;color:var(--text-3);margin-top:6px;line-height:1.5}
    label{display:block;font-size:12px;color:var(--text-3);margin-bottom:6px}
    input[type=text],textarea,select{width:100%;background:var(--surface-deep);border:1px solid var(--border);border-radius:8px;color:var(--text);padding:10px 14px;font-size:14px;font-family:inherit;outline:none;transition:border-color .15s}
    input[type=text]:focus,textarea:focus,select:focus{border-color:var(--accent-border)}
    textarea{min-height:180px;resize:vertical;font-family:'Courier New',monospace;font-size:12px;line-height:1.6}
    select{background:var(--surface-deep)}

    /* ── Buttons ── */
    button{background:var(--accent-dim);color:var(--accent);border:1px solid var(--accent-border);border-radius:7px;padding:10px 20px;font-size:14px;cursor:pointer;font-family:inherit;transition:all .15s}
    button:hover{background:rgba(56,189,248,.2)}
    button.sec{background:var(--surface);color:var(--text-2);border-color:var(--border)}
    button.sec:hover{background:var(--surface-hover)}

    /* ── Two column layout ── */
    .two-col{display:grid;grid-template-columns:1fr 1fr;gap:28px}

    /* ── Table ── */
    table{width:100%;border-collapse:collapse;font-size:13px}
    th{text-align:left;color:var(--text-3);font-size:11px;text-transform:uppercase;letter-spacing:.5px;padding:10px 14px;border-bottom:1px solid var(--border)}
    td{padding:13px 14px;border-bottom:1px solid var(--border-sub);color:var(--text-2);vertical-align:middle}

    /* ── Toggle switches ── */
    .toggle{position:relative;display:inline-block;width:38px;height:20px}
    .toggle input{opacity:0;width:0;height:0}
    .slider{position:absolute;cursor:pointer;inset:0;background:rgba(255,255,255,.12);border-radius:20px;transition:.2s}
    .slider:before{position:absolute;content:"";height:14px;width:14px;left:3px;bottom:3px;background:#fff;border-radius:50%;transition:.2s}
    input:checked+.slider{background:var(--accent)}
    input:checked+.slider:before{transform:translateX(18px)}

    /* ── Code ── */
    .code{font-family:'Courier New',monospace;background:var(--surface-deep);border:1px solid var(--border);border-radius:5px;padding:5px 10px;font-size:11px;color:var(--accent);white-space:nowrap;overflow-x:auto;max-width:300px;display:block}

    /* ── MCP rows ── */
    .mcp-row{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 18px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:flex-start;gap:16px;backdrop-filter:var(--blur)}
    .mcp-row .inf{flex:1}
    .mcp-row .name{font-size:14px;color:var(--text-strong);margin-bottom:4px}
    .mcp-row .mcp-desc{font-size:12px;color:var(--text-3);margin-bottom:3px;line-height:1.4}
    .mcp-row .cost{font-size:11px;color:var(--text-3);font-family:monospace}

    /* ── Sub-tabs ── */
    .tabs{display:flex;gap:6px;margin-bottom:18px}
    .tab{padding:6px 14px;background:var(--surface);border:1px solid var(--border);border-radius:20px;cursor:pointer;font-size:12px;color:var(--text-3);transition:all .15s;backdrop-filter:var(--blur)}
    .tab.active{background:var(--accent-dim);color:var(--accent);border-color:var(--accent-border)}

    /* ── Hint / info box ── */
    .hint{font-size:11px;color:var(--text-3);margin-top:5px;line-height:1.5}
    .info-box{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin-bottom:20px;font-size:12px;color:var(--text-3);line-height:1.6;backdrop-filter:var(--blur)}
    .info-box strong{color:var(--text-2)}

    /* ── Toast ── */
    .toast{position:fixed;bottom:24px;right:24px;background:var(--ok);color:#000;padding:10px 20px;border-radius:8px;font-size:13px;display:none;z-index:999;font-weight:500;box-shadow:0 4px 24px var(--ok-glow)}
    .toast.err{background:var(--err);color:#fff;box-shadow:0 4px 24px var(--err-glow)}

    /* ── Preview pane ── */
    pre#preview{background:var(--surface-deep);border:1px solid var(--border);border-radius:10px;padding:16px;font-size:11px;color:var(--accent);overflow:auto;height:520px;white-space:pre-wrap;font-family:'Courier New',monospace;line-height:1.5}

    /* ── Scope badge variants ── */
    .scope-badge.global{background:var(--accent-dim);color:var(--accent);border-color:var(--accent-border)}

    /* ── Checkbox rows (wizard) ── */
    .cb-row{display:flex;align-items:flex-start;gap:8px;margin-bottom:12px}
    .cb-row input{margin-top:2px;flex-shrink:0}
    .cb-row .cb-label{font-size:13px;color:var(--text-2)}
    .cb-row .cb-help{font-size:11px;color:var(--text-3);margin-top:2px;line-height:1.4}

    /* ── Modal ── */
    .modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:200;display:flex;align-items:center;justify-content:center}
    .modal{background:#0d1117;border:1px solid var(--border);border-radius:12px;width:520px;max-height:520px;display:flex;flex-direction:column;box-shadow:var(--shadow)}
    .modal-header{padding:16px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
    .modal-header h3{margin:0;font-size:14px;color:var(--text-strong)}
    .modal-header button{background:none;border:none;color:var(--text-3);font-size:20px;cursor:pointer;padding:0;line-height:1}
    .modal-header button:hover{color:var(--text-strong)}
    .modal-crumb{padding:10px 20px;border-bottom:1px solid var(--border-sub);font-family:monospace;font-size:12px;color:var(--text-3);background:var(--surface-deep);word-break:break-all}
    .modal-list{flex:1;overflow-y:auto;padding:8px}
    .modal-item{display:flex;align-items:center;gap:10px;padding:9px 12px;border-radius:6px;cursor:pointer;font-size:13px;color:var(--text-2)}
    .modal-item:hover{background:var(--surface-hover);color:var(--text-strong)}
    .modal-item .icon{color:var(--accent);flex-shrink:0;font-size:15px}
    .modal-item.up .icon{color:var(--text-3)}
    .modal-footer{padding:12px 16px;border-top:1px solid var(--border);display:flex;gap:8px;justify-content:flex-end;align-items:center}
    .modal-footer .sel-path{flex:1;font-family:monospace;font-size:11px;color:var(--text-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

    /* ── Project Commander ── */
    .step-progress{display:flex;align-items:center;margin-bottom:24px;max-width:400px}
    .step-dot{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;flex-shrink:0;border:2px solid var(--border);color:var(--text-3);background:var(--surface)}
    .step-dot.active{background:var(--accent-dim);border-color:var(--accent-border);color:var(--accent)}
    .step-dot.done{background:rgba(74,222,128,.15);border-color:rgba(74,222,128,.4);color:var(--ok)}
    .step-line{flex:1;height:2px;background:var(--border)}
    .step-line.done{background:rgba(74,222,128,.4)}
    .step-actions{display:flex;justify-content:space-between;margin-top:24px}
    .step-actions.end{justify-content:flex-end}
    .wizard-steps{display:none}
    .wizard-steps.active{display:block}
    .np-field{margin-bottom:16px}
    .np-slug{font-size:11px;color:var(--text-3);margin-top:3px;font-family:monospace}
    .np-radio-group{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px}
    .np-radio{padding:6px 14px;border:1px solid var(--border);border-radius:6px;cursor:pointer;font-size:13px;color:var(--text-3);background:var(--surface);user-select:none;transition:all .15s}
    .np-radio.active{background:var(--accent-dim);border-color:var(--accent-border);color:var(--accent)}
    .np-check-row{display:flex;align-items:center;gap:8px;margin-bottom:10px;font-size:13px;color:var(--text-2);cursor:pointer}
    .np-result{background:var(--surface-deep);border:1px solid var(--border);border-radius:6px;padding:10px 14px;margin-bottom:10px;font-family:'Courier New',monospace;font-size:12px;color:var(--accent)}
    .np-err{background:rgba(127,29,29,.3);border:1px solid var(--err);border-radius:6px;padding:10px 14px;font-size:12px;color:var(--err);margin-bottom:12px;line-height:1.5}
    .np-ok{color:var(--ok);font-weight:600;font-size:15px;margin-bottom:12px}

    /* ── File manager toolbar ── */
    .fm-toolbar{display:none;padding:6px 12px;border-bottom:1px solid var(--border);gap:6px;flex-wrap:wrap}
    .fm-toolbar.active{display:flex}
    .fm-toolbar .sec{font-size:12px;padding:4px 10px}
    .fm-item-sel{background:var(--accent-dim)!important;color:var(--accent)!important}
    .fm-error{display:none;padding:4px 14px 6px;font-size:12px;color:var(--err)}

    /* ── Update card ── */
    #update-card{max-width:500px;margin-top:16px}
  </style>
```

- [ ] **Step 3: Verify no syntax errors in the Python file**

```bash
python3 -c "import configure" && echo "OK"
```

Expected: `OK`. Fix any Python string escaping issues before continuing.

- [ ] **Step 4: Run tests**

```bash
python3 -m pytest tests/test_configure.py -q 2>&1 | tail -5
```

Expected: same pass count as Task 1 baseline.

---

## Task 3: Replace `<nav>` + add brand-edit panel

**Files:** `configure.py:647–668`

Replace the old `<body>\n<nav>...</nav>` block (which contained the sidebar) with the new top-nav + brand-edit panel. The brand-edit panel moves outside `<nav>` so `toggleBrandEdit()` still works unchanged.

- [ ] **Step 1: Find the nav block**

```bash
grep -n "<nav>\|</nav>\|nav-footer\|brand-edit" configure.py | head -20
```

Note the line range of `<body>` through `</nav>` — this is what gets replaced.

- [ ] **Step 2: Replace the entire nav block**

Find this block in `configure.py` (starts with `<body>` around line 647, ends with `</nav>` around line 668):

```html
<body>
<nav>
  <h1>oculus-configs</h1>
  <a onclick="nav('dashboard',this)" class="active">Dashboard</a>
  <a onclick="nav('newproject',this)">Project Commander</a>
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
```

Replace with:

```html
<body>
<nav>
  <div class="wordmark" id="brand-display">oculus-configs</div>
  <div class="nav-tabs">
    <button class="nav-tab active" onclick="nav('dashboard',this)">Dashboard</button>
    <button class="nav-tab" onclick="nav('newproject',this)">Project Commander</button>
    <button class="nav-tab" onclick="nav('wizard',this)">CLAUDE.md</button>
    <button class="nav-tab" onclick="nav('mcp',this)">MCP Setup</button>
    <button class="nav-tab" onclick="nav('plugins',this)">Plugins</button>
    <button class="nav-tab" onclick="nav('templates',this)">Templates</button>
  </div>
  <div class="nav-right">
    <div class="theme-picker">
      <div class="theme-swatch active" id="sw-aurora" style="background:conic-gradient(#38bdf8,#a78bfa,#34d399,#38bdf8)" onclick="setTheme('aurora')" title="True Aurora"></div>
      <div class="theme-swatch" id="sw-cyan" style="background:#38bdf8" onclick="setTheme('cyan')" title="Sky Cyan"></div>
      <div class="theme-swatch" id="sw-violet" style="background:#a78bfa" onclick="setTheme('violet')" title="Violet"></div>
    </div>
    <button class="icon-btn" onclick="toggleBrandEdit()" title="Edit branding">&#9998;</button>
  </div>
</nav>
<div class="brand-edit" id="brand-edit">
  <input type="text" id="brand-name-input" placeholder="Display name">
  <input type="text" id="brand-logo-input" placeholder="Logo URL (optional)">
  <button onclick="saveBranding()">Save</button>
  <button class="sec" onclick="toggleBrandEdit()">Cancel</button>
</div>
```

- [ ] **Step 3: Verify Python syntax**

```bash
python3 -c "import configure" && echo "OK"
```

- [ ] **Step 4: Run tests**

```bash
python3 -m pytest tests/test_configure.py -q 2>&1 | tail -5
```

---

## Task 4: Update section header markup

**Files:** `configure.py:670–879`

Each `<section>` currently starts with a raw `<h2>` and `<p class="section-desc">`. Wrap them in `<div class="section-header">` so the spec's layout applies. The scope badges change from `.scope-badge.global/.project` to inline style or the new class names.

Do each section one at a time.

- [ ] **Step 1: Dashboard section header**

Find:
```html
<section id="dashboard" class="active">
  <h2>Config Status <span class="scope-badge global">global</span></h2>
  <p class="section-desc">Health of your global Claude Code config in <strong>~/.claude/</strong>. These settings apply to <strong>every project</strong> on this machine. Project-specific rules live in a <code>CLAUDE.md</code> inside each project folder.</p>
```

Replace with:
```html
<section id="dashboard" class="active">
  <div class="section-header">
    <h2>Config Status <span class="scope-badge global">global</span></h2>
    <p class="section-desc">Health of your global Claude Code config in <strong>~/.claude/</strong>. These settings apply to <strong>every project</strong> on this machine. Project-specific rules live in a <code>CLAUDE.md</code> inside each project folder.</p>
  </div>
```

- [ ] **Step 2: CLAUDE.md (wizard) section header**

Find:
```html
<section id="wizard">
  <h2>CLAUDE.md <span class="scope-badge global">global</span></h2>
  <p class="section-desc">Your <strong>~/.claude/CLAUDE.md</strong> — Claude reads this at the start of <em>every</em> session on this machine. Use the Wizard to build it from a form, or Raw Edit to modify it directly.</p>
```

Replace with:
```html
<section id="wizard">
  <div class="section-header">
    <h2>CLAUDE.md <span class="scope-badge global">global</span></h2>
    <p class="section-desc">Your <strong>~/.claude/CLAUDE.md</strong> — Claude reads this at the start of <em>every</em> session on this machine. Use the Wizard to build it from a form, or Raw Edit to modify it directly.</p>
  </div>
```

- [ ] **Step 3: MCP Setup section header**

Find:
```html
<section id="mcp">
  <h2>MCP Setup <span class="scope-badge global">global</span></h2>
  <p class="section-desc"><strong>MCP (Model Context Protocol)</strong> connects Claude to external tools during your sessions. Without it, Claude can only see files you paste in. With it, Claude can read GitHub issues, create PRs, and look up live library docs — automatically. Each server costs tokens every turn it's active, so only enable what you need.</p>
```

Replace with:
```html
<section id="mcp">
  <div class="section-header">
    <h2>MCP Setup <span class="scope-badge global">global</span></h2>
    <p class="section-desc"><strong>MCP (Model Context Protocol)</strong> connects Claude to external tools during your sessions. Without it, Claude can only see files you paste in. With it, Claude can read GitHub issues, create PRs, and look up live library docs — automatically. Each server costs tokens every turn it's active, so only enable what you need.</p>
  </div>
```

- [ ] **Step 4: Plugins section header**

Find:
```html
<section id="plugins">
  <h2>Plugins <span class="scope-badge global">global</span></h2>
  <p class="section-desc">Plugins add workflow skills to Claude Code — things like structured brainstorming, TDD enforcement, and code review checklists. <strong>Installed</strong> means the plugin files are on disk. <strong>Enabled</strong> means Claude actually loads them each session. You can install a plugin but leave it disabled to save overhead.</p>
```

Replace with:
```html
<section id="plugins">
  <div class="section-header">
    <h2>Plugins <span class="scope-badge global">global</span></h2>
    <p class="section-desc">Plugins add workflow skills to Claude Code — things like structured brainstorming, TDD enforcement, and code review checklists. <strong>Installed</strong> means the plugin files are on disk. <strong>Enabled</strong> means Claude actually loads them each session. You can install a plugin but leave it disabled to save overhead.</p>
  </div>
```

- [ ] **Step 5: Templates section header**

Find:
```html
<section id="templates">
  <h2>Project Templates <span class="scope-badge project">per-project</span></h2>
  <p class="section-desc">These templates live in <strong>~/Templates/claude-code-starter/</strong>. Edit them here to change what every new project starts with, then deploy them directly into any project folder.</p>
```

Replace with:
```html
<section id="templates">
  <div class="section-header">
    <h2>Project Templates <span class="scope-badge project">per-project</span></h2>
    <p class="section-desc">These templates live in <strong>~/Templates/claude-code-starter/</strong>. Edit them here to change what every new project starts with, then deploy them directly into any project folder.</p>
  </div>
```

- [ ] **Step 6: Project Commander section header**

Find:
```html
<section id="newproject">
  <h2>Project Commander</h2>
  <p class="section-desc">Create new projects or manage existing folders — rename, delete, move, and create directories anywhere on your machine.</p>
```

Replace with:
```html
<section id="newproject">
  <div class="section-header">
    <h2>Project Commander</h2>
    <p class="section-desc">Create new projects or manage existing folders — rename, delete, move, and create directories anywhere on your machine.</p>
  </div>
```

- [ ] **Step 7: Verify Python syntax**

```bash
python3 -c "import configure" && echo "OK"
```

- [ ] **Step 8: Run tests**

```bash
python3 -m pytest tests/test_configure.py -q 2>&1 | tail -5
```

---

## Task 5: JS — theme system, nav() fix, init update

**Files:** `configure.py` (inside the `<script>` block, around lines 909–1498)

Three JS changes: add the theme system, fix the `nav()` tab selector, update the init IIFE.

- [ ] **Step 1: Add THEMES constant and setTheme() — insert near top of script block**

Find the line `let plugData={};let mcpData={};` (first line of the `<script>` block) and insert the theme system immediately before it:

```js
const THEMES={
  aurora:{
    '--accent':'#38bdf8','--accent-dim':'rgba(56,189,248,.12)',
    '--accent-border':'rgba(56,189,248,.25)','--accent-glow':'rgba(56,189,248,.18)',
    '--wordmark-from':'#38bdf8','--wordmark-to':'#a78bfa',
    '--glow-a':'rgba(56,189,248,.18)','--glow-b':'rgba(139,92,246,.12)',
    '--glow-c':'rgba(16,185,129,.07)','--glow-d':'rgba(56,189,248,.06)',
  },
  cyan:{
    '--accent':'#38bdf8','--accent-dim':'rgba(56,189,248,.12)',
    '--accent-border':'rgba(56,189,248,.25)','--accent-glow':'rgba(56,189,248,.2)',
    '--wordmark-from':'#38bdf8','--wordmark-to':'#7dd3fc',
    '--glow-a':'rgba(56,189,248,.22)','--glow-b':'rgba(14,165,233,.1)',
    '--glow-c':'rgba(56,189,248,.05)','--glow-d':'rgba(56,189,248,.08)',
  },
  violet:{
    '--accent':'#a78bfa','--accent-dim':'rgba(139,92,246,.12)',
    '--accent-border':'rgba(139,92,246,.25)','--accent-glow':'rgba(139,92,246,.2)',
    '--wordmark-from':'#a78bfa','--wordmark-to':'#c4b5fd',
    '--glow-a':'rgba(139,92,246,.22)','--glow-b':'rgba(109,40,217,.12)',
    '--glow-c':'rgba(139,92,246,.05)','--glow-d':'rgba(167,139,250,.07)',
  }
};
function setTheme(name){
  const vars=THEMES[name];if(!vars)return;
  Object.entries(vars).forEach(([k,v])=>document.documentElement.style.setProperty(k,v));
  document.querySelectorAll('.theme-swatch').forEach(s=>s.classList.remove('active'));
  const sw=document.getElementById('sw-'+name);if(sw)sw.classList.add('active');
  localStorage.setItem('oculus-theme',name);
}
```

- [ ] **Step 2: Remove toggleTheme()**

Find and delete this function entirely:
```js
function toggleTheme(){
  const isLight=document.body.classList.toggle('light');
  document.getElementById('theme-btn').textContent=isLight?'☽':'☀';
  localStorage.setItem('theme',isLight?'light':'dark');
}
```

- [ ] **Step 3: Fix the nav() selector**

Find in the `nav()` function:
```js
  document.querySelectorAll('nav a').forEach(a=>a.classList.remove('active'));
```

Replace with:
```js
  document.querySelectorAll('.nav-tab').forEach(a=>a.classList.remove('active'));
```

- [ ] **Step 4: Replace the init IIFE**

Find (near the very end of the script, just before `loadBranding();`):
```js
(function(){var t=localStorage.getItem('theme');if(t==='light'){document.body.classList.add('light');document.getElementById('theme-btn').textContent='☽';}})();
```

Replace with:
```js
setTheme(localStorage.getItem('oculus-theme')||'aurora');
```

- [ ] **Step 5: Verify Python syntax**

```bash
python3 -c "import configure" && echo "OK"
```

- [ ] **Step 6: Run tests**

```bash
python3 -m pytest tests/test_configure.py -q 2>&1 | tail -5
```

Expected: same pass count as baseline. All API tests still green.

---

## Task 6: Visual verification and commit

- [ ] **Step 1: Start the server**

```bash
python3 configure.py &
sleep 1
```

On WSL2 it auto-opens the Windows browser. If not, open `http://localhost:4827` manually.

- [ ] **Step 2: Verify the golden path**

Check each item visually:

| Check | Expected |
|-------|----------|
| Background | Deep dark with colored aurora glows in the corners |
| Top navbar | Glass bar, `OCULUS` gradient wordmark, 6 tabs, 3 swatches top-right |
| Aurora swatch (conic) | Click → cyan+violet glows appear |
| Cyan swatch | Click → single cool-blue glow, wordmark shifts to solid cyan |
| Violet swatch | Click → purple glow, wordmark shifts to violet |
| Dashboard tab | Status cards with glowing dots (green glow on ok, amber on warn) |
| Projects tab | Two glass cards for Create / Manage |
| CLAUDE.md tab | Wizard form + live preview with new button style |
| MCP Setup tab | Glass MCP rows with toggle switches |
| Plugins tab | Table with glowing status dots |
| Templates tab | Sub-tab pills + textarea |
| ✎ button | Brand-edit panel appears below nav |
| Toast | Save any form → toast appears bottom-right with green glow |
| Page reload | Theme persists (stored in localStorage) |

- [ ] **Step 3: Kill the dev server**

```bash
kill %1 2>/dev/null || pkill -f "configure.py" 2>/dev/null
```

- [ ] **Step 4: Final test run**

```bash
python3 -m pytest tests/test_configure.py -v 2>&1 | tail -10
```

Expected: 65 tests pass.

- [ ] **Step 5: Commit**

```bash
git add configure.py
git commit -m "$(cat <<'EOF'
feat: glass/aurora GUI redesign with 3-theme picker

Replace sidebar SPA with top-nav Glass/Aurora design. Frosted glass
surfaces, aurora background via layered radial gradients, glowing status
dots. Theme picker switches between True Aurora (multi-color), Sky Cyan,
and Violet — persisted to localStorage. All API logic unchanged.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review

**Spec coverage check:**
- ✅ CSS-only changes — Python backend untouched
- ✅ Top navigation bar — Task 3
- ✅ Aurora background via `body::before` — Task 2 CSS
- ✅ Glass surfaces (`backdrop-filter`, translucent fills) — Task 2 CSS
- ✅ Glowing status dots — Task 2 CSS (`.dot.ok` etc.)
- ✅ `THEMES` JS object matches `docs/themes.md` token names exactly — Task 5
- ✅ 3 swatches in nav-right — Task 3
- ✅ `localStorage` key `'oculus-theme'` — Task 5
- ✅ Light mode removed — old toggle and `.light` class body variant not included in new CSS
- ✅ `#brand-display` preserved on `.wordmark` — Task 3 (branding JS unchanged)
- ✅ `#brand-edit` preserved — Task 3 (moved outside nav, same IDs)
- ✅ `nav()` selector fix — Task 5

**Placeholder scan:** No TBDs. All code blocks are complete.

**Type/name consistency:** `setTheme()` used consistently in Task 5 step 1, 4 and in swatch `onclick` attributes in Task 3. `THEMES` object keys match CSS var names in the style block. `'oculus-theme'` localStorage key consistent across setTheme() and init line.
