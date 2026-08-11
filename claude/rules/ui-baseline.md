# UI Baseline

**Applies when** building or modifying a user interface: web, desktop, or
mobile. On backend, CLI, infrastructure, or data work, ignore this file
entirely — do not volunteer design commentary where there is no UI.

**This is not a design system.** It is the short list of things that are wrong
in *any* design system if you get them wrong. It constrains correctness, not
looks. For anything about how a UI should look, match the surrounding code.

## Accessibility — non-negotiable

- Contrast ≥ 4.5:1 for body text, ≥ 3:1 for large text and for meaningful
  non-text (icons, borders that carry state). WCAG 2.2 AA.
- Every interactive element has a visible focus indicator, and it does not rely
  on color alone to be perceivable.
- Color is never the sole carrier of meaning — pair it with text, icon, or shape.
- Touch targets ≥ 44×44 CSS px, even when the painted element is smaller.
- Honor `prefers-reduced-motion`: drop transforms and long transitions, keep
  opacity changes.
- Every form control has a programmatic label. Icon-only controls get an
  accessible name.
- Content is reachable and operable by keyboard alone, in a sensible tab order.

## Structure

- Define color, type, spacing, and radius as **tokens** (CSS custom properties,
  a theme object) and have components reference them. A raw hex, a one-off px
  font size, or a bespoke radius inside a component is the defect this rule
  exists to prevent.
- Pair every foreground token with the surface it sits on, so contrast holds by
  construction rather than by inspection.
- Break layout on **container or viewport width, not device**.
- Prose line length 45–75 characters.
- Use the project's existing spacing scale. If it has none, establish one and
  apply it consistently — no magic numbers.

## Choosing a design system

**There is no default, deliberately.** Use whatever the project already uses.
If a project has none and one is needed, ask — adopting a design system is a
product decision, not a technical one, and it is visible to every user.

Material Design 3 is available as a reference *if a project chooses it*:
`~/.claude/rules/ui-material3.md`. That file is not loaded by default. It is
Google's house style — a specific brand language with its own color model,
type scale, and component vocabulary — not a neutral set of best practices.
Do not apply it unasked, and do not treat its absence as a gap.
