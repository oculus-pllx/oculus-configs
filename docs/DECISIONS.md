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

## ADR-008: Codex CLI and Gemini CLI skill ports — parallel directory structure

**Date**: 2026-05-14 (Codex), 2026-05-15 (Gemini)  
**Status**: Accepted

**Decision**: Each CLI gets a top-level directory (`codex/`, `gemini/`) with a global config file (`AGENTS.md` / `GEMINI.md`) and a `skills/` subdirectory containing 8 Superpowers-equivalent SKILL.md files. `install.sh` gets one section per CLI (§8 Codex, §9 Gemini) that detects whether the CLI is installed and copies files to the appropriate home directory (`~/.codex/`, `~/.gemini/`).

**Why**: Mirrors the existing `claude/` pattern — each AI CLI gets its own isolated config namespace. Separate directories prevent cross-contamination if one CLI is uninstalled, and let skill content diverge independently per platform over time.

**Consequences**: Skill content is duplicated between `codex/skills/` and `gemini/skills/` (not shared). Cross-references within skill files (e.g. systematic-debugging → test-driven-development) are path-specific to each CLI (`~/.codex/skills/` vs `~/.gemini/skills/`). Syncing content updates across CLIs is manual.

---

## ADR-009: Lazy skill loading via read-file triggers, not eager includes

**Date**: 2026-05-15  
**Status**: Accepted

**Decision**: Neither `AGENTS.md` nor `GEMINI.md` includes skill content at session start. Instead, they instruct the CLI to read the relevant SKILL.md file (`cat ~/.codex/skills/<name>/SKILL.md` / `read_file ~/.gemini/skills/<name>/SKILL.md`) only when a workflow trigger fires.

**Why**: Loading all 8 skills upfront would add ~15–20k tokens of context per session. Skills are situational — brainstorming fires before feature work, systematic-debugging fires when stuck. Most sessions never need most skills.

**Consequences**: Skill content is not available until triggered. This is intentional — the trigger IS the activation.

---

## ADR-010: Glass/Aurora GUI redesign — CSS custom property theme system

**Date**: 2026-05-22
**Status**: Accepted

**Decision**: Replace the flat dark sidebar UI in `configure.py` with a glass/aurora aesthetic: top navigation bar, frosted glass surfaces (`backdrop-filter: blur(12px)`), and a `body::before` aurora background built from 4 layered `radial-gradient` calls driven by CSS custom properties (`--glow-a/b/c/d`). Three themes (True Aurora, Sky Cyan, Violet) are defined as a `THEMES` JS constant and switched via `document.documentElement.style.setProperty()`. Active theme persists to `localStorage` under key `'oculus-theme'`.

**Why**: The previous UI was functional but visually generic. The aurora effect is distinctive, the CSS custom property architecture makes theme switching zero-JS-DOM-manipulation (just property writes), and the `body::before` technique keeps the gradient off the content stacking context entirely — no z-index conflicts. The design is also portable: `docs/themes.md` is a standalone data sheet for reusing the aurora system on other projects.

**Consequences**: Light mode removed (aurora is always dark). All surfaces must set `position: relative; z-index: 1` to appear above the pseudo-element aurora layer. `backdrop-filter` has no effect if the parent has `overflow: hidden` — avoid that combination on glass cards.
