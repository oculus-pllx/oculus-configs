# Architecture Decision Log

## ADR-001: Single-file Python stdlib server (configure.py)

**Date**: 2026-05-13  
**Status**: Accepted

**Decision**: The local config UI is a single Python 3 file using only stdlib. No pip dependencies.

**Why**: The target environment (WSL, macOS, Linux standalone) may not have pip or a venv. `python3 configure.py` must be the entire install. Zero friction is the feature.

**Consequences**: All HTML/CSS/JS is embedded as a string constant. UI is not hot-reloadable during development. Acceptable for a local tool used infrequently.

---

## ADR-002: Port 4827 for configure.py

**Date**: 2026-05-13  
**Status**: Accepted

**Decision**: Local server binds to port 4827.

**Why**: User explicitly wanted an obscure port to avoid collisions with common dev servers (3000, 8080, etc.). 4827 has no well-known service assignment.

---

## ADR-003: Copy-based install, not symlinks

**Date**: 2026-05-13  
**Status**: Accepted

**Decision**: `install.sh` copies files from the repo into `~/.claude/`. No symlinks.

**Why**: Symlinks require the repo to stay present at the same path. On a new machine the clone path may differ. Copies are self-contained — remove the repo and the config still works. CCC will pull config files independently anyway.

---

## ADR-004: enabledPlugins-only writes for plugin toggles

**Date**: 2026-05-13  
**Status**: Accepted

**Decision**: `update_enabled_plugins()` merges only into the `enabledPlugins` key of `settings.json`. All other keys (hooks, theme, etc.) are untouched.

**Why**: `settings.json` is the single source of truth for Claude Code state. Overwriting the whole file would clobber hooks and other settings the user has configured independently.

---

## ADR-005: configure.py is standalone; CCC absorbs the frontend separately

**Date**: 2026-05-13  
**Status**: Accepted

**Decision**: The HTML/JS in configure.py makes no assumptions about a backend framework. The REST API maps cleanly to whatever CCC uses.

**Why**: CCC is a Proxmox LXC container project (https://github.com/oculus-pllx/CCC) with its own management GUI. The frontend here can be extracted verbatim into that project. No coupling assumptions made in configure.py.

---

## ADR-006: docs/ layout — specs in docs/specs/, plans in docs/plans/

**Date**: 2026-05-13  
**Status**: Accepted

**Decision**: Design specs go in `docs/specs/`, implementation plans in `docs/plans/`. Not under `docs/superpowers/` (the Superpowers plugin default).

**Why**: `docs/superpowers/` looks like plugin-owned territory and confuses readers. Project artifacts should be navigable without knowing the tooling that generated them.

---

## ADR-007: New Project wizard uses subprocess for git/gh, not a Python git library

**Date**: 2026-05-13  
**Status**: Planned

**Decision**: The New Project wizard will call `git` and optionally `gh` via `subprocess.run()` — no third-party Python git library.

**Why**: No pip available on this system. `git` and `gh` are already present on any developer machine this tool targets. `subprocess.run(["git", "init"], cwd=path)` is readable and sufficient.

**Consequences**: Errors surface as stderr strings rather than typed exceptions. The wizard checks for `gh` with `shutil.which("gh")` before offering GitHub repo creation, degrades gracefully to manual remote URL input if absent.

---

## Future: Codex CLI configs (codex/) and Gemini CLI configs (gemini/)

**Date**: 2026-05-13  
**Status**: Planned (not started)

**Decision**: When Codex and Gemini CLI support is added, each gets a top-level directory (`codex/`, `gemini/`) following the same pattern as `claude/` — config files + an install script section.
