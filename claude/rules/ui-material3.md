# UI Baseline — Material Design 3

**Applies when** building or modifying a user interface: web, desktop, or
mobile. On backend, CLI, infrastructure, or data work, ignore this file
entirely — do not volunteer design commentary where there is no UI.

Material Design 3 (M3) is the default design system for new UI. It is a
baseline, not a cage: a project whose own `CLAUDE.md` names a different system
(Tailwind defaults, shadcn/ui, Bootstrap, an in-house kit) overrides this file.
Match the surrounding code before importing anything from here.

Values below are M3 spec figures in dp/sp. On the web, treat 1dp = 1px and
1sp = 1rem/16.

---

## Color — use semantic roles, never raw hex

Never hardcode a color in a component. Reference a role, so light/dark and
theming work without touching component code.

| Role | Purpose |
|---|---|
| `primary` / `on-primary` | Main actions, active states |
| `primary-container` / `on-primary-container` | Standout fills that aren't the main action |
| `secondary` / `tertiary` (+ containers) | Supporting accents, balance |
| `surface` / `on-surface` | Default background and text |
| `surface-variant` / `on-surface-variant` | Subordinate fills, icons, secondary text |
| `surface-container-{lowest,low,,high,highest}` | Elevation-tinted backgrounds |
| `outline` / `outline-variant` | Borders; decorative dividers |
| `error` / `on-error` (+ container) | Validation and destructive states |
| `inverse-surface` / `inverse-on-surface` | Snackbars, tooltips |

Roles come from tonal palettes (tones 0–100). Standard mappings:

| Role | Light | Dark |
|---|---|---|
| `primary` | T40 | T80 |
| `on-primary` | T100 | T20 |
| `primary-container` | T90 | T30 |
| `on-primary-container` | T10 | T90 |
| `surface` | N98 | N6 |
| `on-surface` | N10 | N90 |
| `outline` | NV50 | NV60 |

**Always pair a role with its `on-` counterpart.** Doing so satisfies contrast
by construction; mixing across pairs is how contrast bugs get shipped.

## Typography — five roles, three sizes each

| Role | L | M | S |
|---|---|---|---|
| Display | 57/64 | 45/52 | 36/44 |
| Headline | 32/40 | 28/36 | 24/32 |
| Title | 22/28 | 16/24 | 14/20 |
| Body | 16/24 | 14/20 | 12/16 |
| Label | 14/20 | 12/16 | 11/16 |

Format is `size/line-height` in sp. Body M (14/20) is the default for UI text;
Body L (16/24) for reading-length prose. Label roles are for buttons, tabs, and
form labels — not for paragraphs. Do not invent intermediate sizes.

## Shape

| Token | Radius | Typical use |
|---|---|---|
| none | 0 | Full-bleed surfaces |
| extra-small | 4dp | Snackbars, menus |
| small | 8dp | Chips, text fields |
| medium | 12dp | Cards |
| large | 16dp | Sheets, nav drawers, FAB |
| extra-large | 28dp | Dialogs, large FAB |
| full | 50% | Buttons, pills, avatars |

## Elevation

Levels 0–5 map to 0, 1, 3, 6, 8, 12dp. In M3 elevation is expressed primarily
as a **surface-container tint**, with shadow secondary — do not reach for heavy
drop shadows to signal hierarchy. Resting states: cards 0–1, FAB 3, dialogs 3,
menus 2, nav bar 2.

## Motion

| Purpose | Duration | Easing |
|---|---|---|
| Small utility (hover, toggle) | 100–200ms | standard |
| Standard transitions | 300ms | `cubic-bezier(0.2, 0, 0, 1)` |
| Emphasized / hero | 500ms | `cubic-bezier(0.05, 0.7, 0.1, 1)` |
| Exits | 200ms | accelerate |

Enter decelerates, exit accelerates. Honor `prefers-reduced-motion`: drop
transforms and long transitions, keep opacity changes.

## Layout — window size classes

| Class | Width | Panes | Margin | Navigation |
|---|---|---|---|---|
| Compact | <600dp | 1 | 16dp | Bottom bar |
| Medium | 600–839 | 1 | 24dp | Nav rail |
| Expanded | 840–1199 | 2 | 24dp | Nav rail |
| Large | 1200–1599 | 2 | 24dp | Rail or drawer |
| Extra-large | ≥1600 | 2–3 | 24dp | Drawer |

Break on **window size class, not device**. Pane gutter 24dp. Spacing is a 4dp
grid — 8dp is the common step; 4dp for tight pairings. No magic numbers.

Canonical layouts, in preference order over bespoke arrangements:
**list-detail** (browse + inspect), **supporting pane** (primary + secondary
context), **feed** (equivalent items in a grid).

## Non-negotiables

- Touch targets ≥ 48×48dp, even when the visual element is smaller.
- Contrast ≥ 4.5:1 body text, ≥ 3:1 large text and meaningful non-text.
- Line length 45–75 characters for prose.
- Visible, non-color focus indicators on every interactive element.
- State layers on interactive surfaces: hover 8%, focus 10%, pressed 10%.
- Color is never the sole carrier of meaning — pair with icon, text, or shape.

## Applying this

1. Define color roles, type scale, shape, and spacing as **tokens** (CSS custom
   properties, a theme object) before building components.
2. Components consume tokens only. A raw hex, px font size, or one-off radius
   inside a component is the defect this file exists to prevent.
3. When the user asks for a look that conflicts with M3, follow the user and
   say briefly what diverged — do not silently re-impose the baseline.
