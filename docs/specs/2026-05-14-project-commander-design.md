# Project Commander Design

**Date**: 2026-05-14  
**Status**: Approved  
**ADRs**: 001 (stdlib only), 007 (subprocess for git/gh)

---

## Overview

Expand the "New Project" tab into **Project Commander** — a hub for creating and managing project folders. The existing 4-step wizard handles creation. A new "Manage Existing" entry point opens the browse modal in **file manager mode**, enabling rename, delete, move, and new folder operations on any directory.

The browse modal is the engine. Project Commander is the cockpit. File management is available anywhere file browsing is available — no new nav section required.

---

## Architecture

### Approach

**Upgrade the browse modal to dual-mode** (Approach A):

| Mode | Triggered by | Behavior |
|------|-------------|----------|
| Picker | `openBrowse(callback)` | Single-click navigates; "Select" confirms; no toolbar |
| Manager | `openBrowse()` (no callback) | Single-click selects; double-click navigates; toolbar shown; "Select" hidden |

No existing call sites change. No new nav items. File management is reachable from Project Commander and from any future "Browse" button that omits the callback.

### New Backend Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/fs/rename` | Rename a folder (`path`, `new_name`) |
| POST | `/api/fs/delete` | Delete a folder recursively (`path`) |
| POST | `/api/fs/mkdir` | Create a new folder (`parent`, `name`) |
| POST | `/api/fs/move` | Move a folder to a new parent (`src`, `dest`) |

All return `{"ok": true}` or `{"ok": false, "error": "..."}`.

Existing `GET /api/browse` handles directory listing (unchanged).

### Protected Paths

The backend maintains a deny-list — operations on these paths return an error:
- `Path.home()` (the home directory itself)
- `CLAUDE_DIR` (`~/.claude`)
- The repo root (`configure.py`'s own directory)

---

## Components

### Project Commander Tab

Rename nav entry from "New Project" to "Project Commander". Tab shows two equal-weight cards:

- **Create New Project** — launches the existing 4-step wizard
- **Manage Existing** — calls `openBrowse()` with no callback, opening the modal in manager mode

### Browse Modal — Manager Mode

**Selection model:**
- Single-click: highlights folder (selected state), no navigation
- Double-click: navigates into folder
- "↑ Up" button: navigates to parent (unchanged)
- Status bar at bottom: shows selected folder path

**Toolbar** (visible only in manager mode, above the file list):

| Button | Enabled when | Behavior |
|--------|-------------|----------|
| New Folder | Always | Inline input at top of list; Enter confirms, Esc cancels |
| Rename | Folder selected | Inline editable input replaces folder name; Enter confirms |
| Delete | Folder selected | Confirmation dialog — user must type `delete`; then `shutil.rmtree()` |
| Move | Folder selected | Opens a second picker-mode modal instance; user navigates to destination; "Move Here" button confirms |

**Picker mode** (callback provided): toolbar completely hidden; single-click still navigates; "Select" button present. No regressions.

### Backend Functions

```python
def fs_rename(path: str, new_name: str) -> dict
def fs_delete(path: str) -> dict
def fs_mkdir(parent: str, name: str) -> dict
def fs_move(src: str, dest: str) -> dict
```

All validate against the protected-paths deny-list before operating. `fs_delete` uses `shutil.rmtree()`. `fs_move` uses `shutil.move()`. `fs_rename` uses `Path.rename()`. `fs_mkdir` uses `Path.mkdir()`.

---

## Error Handling

Frontend shows an inline error message below the toolbar (not a blocking dialog). File list stays intact — user can retry without reopening.

| Operation | Error cases |
|-----------|-------------|
| New Folder | Name already exists; empty name |
| Rename | Name conflict at same level; empty name |
| Delete | Path not found; protected path |
| Move | Name conflict at destination; src equals dest; protected path |

---

## Testing

Target: ~35 unit tests total (up from 25). New test classes in `tests/test_configure.py`:

| Class | Tests |
|-------|-------|
| `TestFsMkdir` | success; already exists |
| `TestFsRename` | success; name conflict; empty name |
| `TestFsDelete` | success; path not found; protected path blocked |
| `TestFsMove` | success; name conflict at destination |

Existing `TestHtmlJs` (JS syntax check) covers modal JS changes automatically.

TDD order: write failing test → implement minimal code → pass → commit.

---

## Scope / Out of Scope

**In scope:**
- Rename "New Project" nav + tab to "Project Commander"
- Two entry cards (Create / Manage)
- Browse modal manager mode with full toolbar
- Four backend fs endpoints
- Unit tests for all backend functions

**Out of scope (future):**
- File operations (only folders)
- Copy folder
- Keyboard shortcuts in the file manager
- Context menu (right-click)
- Drag-and-drop move
