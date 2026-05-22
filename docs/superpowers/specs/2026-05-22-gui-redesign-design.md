# GUI Redesign — Design Spec
**Date**: 2026-05-22  
**Status**: Approved  
**Scope**: `configure.py` embedded HTML/CSS/JS (the local web UI at port 4827)

---

## Summary

Replace the current utilitarian dark sidebar SPA with a Glass/Aurora aesthetic featuring a top navigation bar, frosted glass surfaces, and a 3-theme picker (True Aurora, Sky Cyan, Violet). The `THEMES` JS object doubles as the canonical theme data sheet — the same source of truth for the UI and for `docs/themes.md`.

---

## What Changes

| Area | Current | New |
|------|---------|-----|
| Navigation | 200px left sidebar, text links | Fixed top nav bar, tab-style links |
| Background | Flat `#0f0f0f` | Deep dark + multi-color radial aurora glows via `::before` pseudo-element |
| Surfaces | Flat `#1a1a1a` cards | `rgba(255,255,255,0.04)` + `backdrop-filter: blur(12px)` |
| Borders | Solid `#2a2a2a` | `rgba(255,255,255,0.08)` — feels recessed into the glow |
| Status dots | Plain colored circles | Colored circles + matching `box-shadow` glow |
| Accent color | Hard-coded `#2563eb` | CSS custom property `--accent`, swapped per theme |
| Light mode | Full light theme via `body.light` | Removed — aurora is always dark |
| Theme system | Single toggle (dark/light) | 3-swatch picker in top-right: True Aurora, Sky Cyan, Violet |
| Wordmark | Plain text `"oculus-configs"` | Gradient text via `--wordmark-from` / `--wordmark-to` |
| Section titles | Plain `h2` | `h2` + scope badge (global / per-project) |
| Buttons | Solid `#2563eb` fill | Translucent accent-tinted with border (`accent-dim` + `accent-border`) |

---

## Theme System Architecture

Themes are defined as a single JS constant in the `<script>` block:

```js
const THEMES = {
  aurora: { /* multi-color — see docs/themes.md */ },
  cyan:   { /* sky blue mono */ },
  violet: { /* indigo/purple mono */ },
};
```

`setTheme(name)` iterates the object and calls `document.documentElement.style.setProperty(k, v)` for each token. The active theme is persisted to `localStorage` under key `'oculus-theme'`. Default is `'aurora'`.

The 3 swatches sit in the navbar right-side controls. The aurora swatch uses `conic-gradient(#38bdf8, #a78bfa, #34d399, #38bdf8)` to suggest the multi-color effect.

---

## Layout

```
┌─────────────────────────────────────────────────────────────┐
│ OCULUS  Dashboard  Projects  CLAUDE.md  MCP  Plugins  Tmpl  [◐ ● ●]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Section heading  [scope badge]                             │
│  Section description — one line, muted                      │
│                                                             │
│  [content area — full width, scrollable]                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

- Navbar: `height: 52px`, `backdrop-filter: blur(12px)`, `background: rgba(8,12,18,0.6)`, `border-bottom: 1px solid rgba(255,255,255,0.08)`
- Active tab: `color: var(--accent)`, `border-bottom: 2px solid var(--accent)` flush with nav bottom edge
- Main area: `padding: 32px 36px`, overflow-y scroll

---

## Aurora Background Technique

Applied as a `body::before` pseudo-element (fixed, full-viewport, `z-index:0`, `pointer-events:none`):

```css
background:
  radial-gradient(ellipse 60% 40% at 80% 10%,  var(--glow-a) 0%, transparent 60%),
  radial-gradient(ellipse 40% 30% at 20% 80%,  var(--glow-b) 0%, transparent 55%),
  radial-gradient(ellipse 50% 35% at 50% 50%,  var(--glow-c) 0%, transparent 65%),
  radial-gradient(ellipse 30% 25% at 10% 20%,  var(--glow-d) 0%, transparent 50%);
transition: background 0.5s ease;
```

Each theme sets `--glow-a` through `--glow-d` to different RGBA colors, so switching themes cross-fades the background aurora.

---

## CSS Token Reference

Base tokens (theme-independent):

| Token | Value | Purpose |
|-------|-------|---------|
| `--bg` | `#080c12` | Page background |
| `--surface` | `rgba(255,255,255,0.04)` | Card / panel fill |
| `--surface-hover` | `rgba(255,255,255,0.07)` | Hover state |
| `--surface-deep` | `rgba(0,0,0,0.25)` | Input / code background |
| `--border` | `rgba(255,255,255,0.08)` | Primary border |
| `--border-sub` | `rgba(255,255,255,0.05)` | Table row dividers |
| `--text` | `rgba(255,255,255,0.82)` | Body text |
| `--text-2` | `rgba(255,255,255,0.6)` | Secondary text |
| `--text-3` | `rgba(255,255,255,0.38)` | Muted / labels |
| `--text-strong` | `#fff` | Headings |
| `--ok` | `#4ade80` | Success green |
| `--ok-glow` | `rgba(74,222,128,0.4)` | Success dot glow |
| `--warn` | `#fbbf24` | Warning amber |
| `--warn-glow` | `rgba(251,191,36,0.3)` | Warning dot glow |
| `--err` | `#f87171` | Error red |
| `--err-glow` | `rgba(248,113,113,0.3)` | Error dot glow |
| `--blur` | `blur(12px)` | Backdrop blur shorthand |
| `--shadow` | `0 8px 32px rgba(0,0,0,0.5)` | Card shadow |

Theme-switched tokens: see `docs/themes.md`.

---

## Components

### Status cards
Glass cards with `backdrop-filter`. Status dot gets a matching `box-shadow` glow. Warn/error states tint the card background (`rgba(251,191,36,0.04)`) and border color (`rgba(251,191,36,0.25)`).

### Buttons
Two variants: `.primary` (accent-tinted fill + accent border) and `.sec` (surface fill, muted text). No solid-color buttons — everything is translucent with backdrop blur.

### Sub-tabs (Wizard, Templates)
Pill-shaped sub-tabs replace the current rectangular tabs. Active state uses `accent-dim` fill + `accent-border`.

### Scope badges
Inline next to `h2`. Global sections: cyan tint. Per-project sections: green tint (`rgba(74,222,128,…)`).

### Toggle switches
Unchanged functionally. Track color changes to `var(--accent)` when checked.

---

## What Does NOT Change

- All API endpoints and Python backend logic — untouched
- All section content (forms, tables, wizard steps, file manager modal)
- The file manager / browse modal
- New project wizard steps
- All JS application logic
- `localStorage` keys for theme persistence (adding `'oculus-theme'`, keeping existing keys if any)

The redesign is purely the `HTML` constant in `configure.py` — specifically the `<style>` block, the `<nav>` element, the section `<h2>` / description markup, and the theme-switching JS.

---

## Files to Change

| File | Change |
|------|--------|
| `configure.py` | Replace `HTML` string: new `<style>`, new `<nav>`, updated section headers, theme JS |
| `docs/themes.md` | New file — standalone theme data sheet |

---

## Out of Scope

- Light mode (removed; aurora is always dark)
- Structural changes to Python API layer
- New sections or features
- Mobile responsiveness (local tool, desktop only)
