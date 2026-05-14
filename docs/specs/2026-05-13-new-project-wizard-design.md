# Design Spec: New Project Wizard

**Date**: 2026-05-13  
**Status**: Approved  
**Scope**: 4-step wizard in `configure.py` for scaffolding new projects from the browser UI

---

## Problem

Creating a new Claude Code project requires manually making a folder, copying template files, running `git init`, and optionally setting up a GitHub remote. The wizard eliminates that friction — zero terminal interaction from idea to committed repo.

## Non-Goals

- No support for monorepos or workspaces
- No template authoring (use the existing Templates tab for that)
- No CI/CD setup
- GitHub Actions, branch protection, and other repo settings are out of scope

---

## Nav Placement

"New Project" is the second item in the sidebar nav, between Dashboard and CLAUDE.md. It signals a primary action without disrupting the config-tool ordering of the remaining tabs.

```
Dashboard
New Project   ← here
CLAUDE.md
MCP Setup
Plugins
Templates
```

---

## Wizard Flow — 4 Steps

All steps are rendered inside a single `<section id="newproject">`. JS manages which step is visible via `showStep(n)`. State accumulates in a plain `wizardState` object — no server round-trips until "Create Project" is clicked.

### Step 1 — Name & Location

- **Project name** text input. Slugified live: `name.toLowerCase().replace(/[^a-z0-9-]/g, '-')`. Slug preview shown beneath field.
- **Parent folder** path field + 📂 button. Reuses the existing `folderBrowserModal` component from the Templates tab.
- **Validation**: "Next" disabled until both fields are non-empty. Invalid characters are silently replaced by the slug — no error message needed.

### Step 2 — Templates

Four checkboxes for which starter files to copy into the new project:

| File | Default |
|------|---------|
| `CLAUDE.md` | ✅ checked |
| `docs/DECISIONS.md` | ✅ checked |
| `.gitignore` | ✅ checked |
| `mcp.json` | ☐ unchecked |

No server call on this step. Selection is recorded in `wizardState.templates[]`.

### Step 3 — Git + GitHub

On section load, `GET /api/which/gh` is called once and cached in `wizardState.caps`:

```json
{ "gh": true, "code": true }
```

**GitHub remote options** (shown based on caps):

- If `gh` available: `● gh create | ○ Manual URL | ○ Skip`
- If not: `● Manual URL | ○ Skip` (gh create option absent)

**Visibility subfields**:
- "gh create" selected → show `● Private | ○ Public` toggle
- "Manual URL" selected → show remote URL text input

"Create Project" triggers:
1. `POST /api/projects/create`
2. If "gh create": `POST /api/projects/github`

### Step 4 — Success

Displays after both backend calls complete:

- **Path** — monospace display of the created folder path
- **Git log** — `git log --oneline` output
- **Clone command** — shown if GitHub remote was set up; copy-to-clipboard button
- **Open in VS Code** — shown only if `wizardState.caps.code === true`; calls `POST /api/projects/open-vscode`
- **+ New Project** — resets `wizardState` and returns to step 1

---

## API Endpoints

### `GET /api/which/gh`

Checks tool availability. Called once on section load.

**Response:**
```json
{ "gh": true, "code": false }
```

### `POST /api/projects/create`

**Request:**
```json
{
  "name": "my-new-project",
  "parent": "/home/peyton/projects",
  "templates": ["CLAUDE.md", "docs/DECISIONS.md", ".gitignore"]
}
```

**Success response:**
```json
{ "ok": true, "path": "/home/peyton/projects/my-new-project", "git_log": "abc1234 Initial commit" }
```

**Error response:**
```json
{ "ok": false, "error": "Folder already exists" }
```

Backend steps (in order):
1. Resolve `path = parent / slugify(name)`
2. Check path doesn't exist — return error if it does
3. `path.mkdir(parents=True)`
4. Copy selected template files from `~/Templates/claude-code-starter/`
5. `subprocess.run(["git", "init", "-b", "main"], cwd=path)`
6. `subprocess.run(["git", "add", "-A"], cwd=path)`
7. `subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=path)`
8. Return `{ok, path, git_log}`

### `POST /api/projects/github`

**Request:**
```json
{ "path": "/home/peyton/projects/my-new-project", "repo_name": "my-new-project", "private": true }
```

**Success response:**
```json
{ "ok": true, "clone_url": "git@github.com:user/my-new-project.git" }
```

**Error response:**
```json
{ "ok": false, "error": "gh: HTTP 422 — name already taken" }
```

Backend steps:
1. `subprocess.run(["gh", "repo", "create", repo_name, "--private/--public", "--source", path, "--push"])`
2. Parse stdout for clone URL
3. Return `{ok, clone_url}` or `{ok: false, error: stderr}`

### `POST /api/projects/remote`

Used when the user selects "Manual URL" in step 3.

**Request:**
```json
{ "path": "/home/peyton/projects/my-new-project", "remote_url": "git@github.com:user/my-new-project.git" }
```

**Success response:**
```json
{ "ok": true, "clone_url": "git@github.com:user/my-new-project.git" }
```

Backend steps:
1. `subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=path)`
2. `subprocess.run(["git", "push", "-u", "origin", "main"], cwd=path)`
3. Return `{ok, clone_url}` or `{ok: false, error: stderr}`

---

### `POST /api/projects/open-vscode`

**Request:**
```json
{ "path": "/home/peyton/projects/my-new-project" }
```

Runs `subprocess.Popen(["code", path])` — non-blocking. Always returns `{ok: true}`.

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Name/parent empty | "Next" button disabled — can't proceed |
| Folder already exists | Red inline error on step 3; user goes Back to change name/parent |
| `git` subprocess fails | Step 4 shows red error block with stderr; path shown for manual recovery |
| `gh` fails (auth, name conflict) | Step 4 shows partial success: local project green, GitHub push red with error |
| `gh` / `code` not in PATH | Checked at section load; options never appear if unavailable |

---

## Implementation Notes

- Uses `subprocess.run()` throughout — no pip, no third-party git library (ADR-007)
- Default branch: `main` (passed via `git init -b main`)
- `folderBrowserModal` reused from Templates tab — no new modal component needed
- `GET /api/which/gh` cached in `wizardState.caps` — not re-checked on each step transition

---

## Tests

New tests in `tests/test_configure.py`:

| Test | Asserts |
|------|---------|
| `test_project_create_success` | Folder exists, templates copied, one commit in git log |
| `test_project_create_folder_exists` | `{ok: false, error: "Folder already exists"}` |
| `test_project_create_no_templates` | Only `.git/` present, git init still ran |
| `test_which_gh` | Response has `gh` and `code` boolean keys |
| `test_project_github_no_gh` | Returns useful error when `gh` not in PATH |

`gh repo create` integration is not unit tested — requires auth and network.  
JS syntax covered by existing `node --check configure.py` test.
