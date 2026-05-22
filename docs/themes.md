# Aurora Theme System — Data Sheet
**Origin**: oculus-configs GUI redesign (2026-05-22)  
**Portable**: drop the CSS variables and JS object into any dark web UI

---

## How It Works

Three CSS custom properties groups control the entire look:

1. **Accent tokens** — interactive color (links, active states, buttons, borders)
2. **Aurora glow tokens** — the `body::before` background radial gradients
3. **Wordmark tokens** — gradient direction of logo/brand text

Switch themes by overwriting these ~10 variables on `:root`. Everything else (surfaces, text, status colors) is theme-neutral.

---

## Base Tokens (theme-neutral — copy these once)

```css
:root {
  --bg:            #080c12;
  --surface:       rgba(255,255,255,0.04);
  --surface-hover: rgba(255,255,255,0.07);
  --surface-deep:  rgba(0,0,0,0.25);
  --border:        rgba(255,255,255,0.08);
  --border-sub:    rgba(255,255,255,0.05);
  --text:          rgba(255,255,255,0.82);
  --text-2:        rgba(255,255,255,0.60);
  --text-3:        rgba(255,255,255,0.38);
  --text-strong:   #ffffff;
  --ok:            #4ade80;
  --ok-glow:       rgba(74,222,128,0.40);
  --warn:          #fbbf24;
  --warn-glow:     rgba(251,191,36,0.30);
  --err:           #f87171;
  --err-glow:      rgba(248,113,113,0.30);
  --blur:          blur(12px);
  --shadow:        0 8px 32px rgba(0,0,0,0.5);
}
```

---

## Theme Tokens

### True Aurora (multi-color — the signature look)

```css
:root {
  --accent:         #38bdf8;
  --accent-dim:     rgba(56,189,248,0.12);
  --accent-border:  rgba(56,189,248,0.25);
  --accent-glow:    rgba(56,189,248,0.18);
  --wordmark-from:  #38bdf8;   /* cyan */
  --wordmark-to:    #a78bfa;   /* violet */

  /* Aurora background — 4 overlapping radial glows */
  --glow-a: rgba(56,189,248,0.18);   /* cyan    — top-right */
  --glow-b: rgba(139,92,246,0.12);   /* violet  — bottom-left */
  --glow-c: rgba(16,185,129,0.07);   /* emerald — center */
  --glow-d: rgba(56,189,248,0.06);   /* cyan    — top-left accent */
}
```

**Swatch**: `conic-gradient(#38bdf8, #a78bfa, #34d399, #38bdf8)`

---

### Sky Cyan (mono-cool)

```css
:root {
  --accent:         #38bdf8;
  --accent-dim:     rgba(56,189,248,0.12);
  --accent-border:  rgba(56,189,248,0.25);
  --accent-glow:    rgba(56,189,248,0.20);
  --wordmark-from:  #38bdf8;
  --wordmark-to:    #7dd3fc;

  --glow-a: rgba(56,189,248,0.22);
  --glow-b: rgba(14,165,233,0.10);
  --glow-c: rgba(56,189,248,0.05);
  --glow-d: rgba(56,189,248,0.08);
}
```

**Swatch**: `#38bdf8`

---

### Violet / Indigo

```css
:root {
  --accent:         #a78bfa;
  --accent-dim:     rgba(139,92,246,0.12);
  --accent-border:  rgba(139,92,246,0.25);
  --accent-glow:    rgba(139,92,246,0.20);
  --wordmark-from:  #a78bfa;
  --wordmark-to:    #c4b5fd;

  --glow-a: rgba(139,92,246,0.22);
  --glow-b: rgba(109,40,217,0.12);
  --glow-c: rgba(139,92,246,0.05);
  --glow-d: rgba(167,139,250,0.07);
}
```

**Swatch**: `#a78bfa`

---

## Aurora Background — Copy-Paste Snippet

This is the core of the effect. Put it on `body::before` (or any full-viewport element):

```css
body {
  background: #080c12;  /* base — must be dark */
  position: relative;
}

body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(ellipse 60% 40% at 80% 10%,  var(--glow-a) 0%, transparent 60%),
    radial-gradient(ellipse 40% 30% at 20% 80%,  var(--glow-b) 0%, transparent 55%),
    radial-gradient(ellipse 50% 35% at 50% 50%,  var(--glow-c) 0%, transparent 65%),
    radial-gradient(ellipse 30% 25% at 10% 20%,  var(--glow-d) 0%, transparent 50%);
  transition: background 0.5s ease;
}

/* Everything on top of the aurora must set position + z-index */
nav, main, .your-content { position: relative; z-index: 1; }
```

**Key parameters:**
- `ellipse W% H% at X% Y%` — shape and position of each glow. Vary X/Y to place glows asymmetrically.
- `transparent 60%` — how far the glow fades out. Lower = tighter, more intense. 60–70% is natural.
- Opacity in the RGBA is the main dial for intensity. Start at 0.15–0.20 for the primary glow (a), lower for the rest.
- `transition: background 0.5s` — enables smooth cross-fade when CSS vars are updated.

---

## Glass Surface Snippet

```css
.glass-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.glass-card:hover {
  border-color: rgba(255,255,255,0.12);
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
```

**Note**: `backdrop-filter` requires the parent not to have `overflow:hidden` or the blur won't show. The element behind must have visible content (the aurora pseudo-element counts).

---

## Gradient Wordmark

```css
.wordmark {
  background: linear-gradient(90deg, var(--wordmark-from), var(--wordmark-to));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

---

## JS Theme Switcher (drop-in)

```js
const THEMES = {
  aurora: {
    '--accent':        '#38bdf8',
    '--accent-dim':    'rgba(56,189,248,0.12)',
    '--accent-border': 'rgba(56,189,248,0.25)',
    '--accent-glow':   'rgba(56,189,248,0.18)',
    '--wordmark-from': '#38bdf8',
    '--wordmark-to':   '#a78bfa',
    '--glow-a': 'rgba(56,189,248,0.18)',
    '--glow-b': 'rgba(139,92,246,0.12)',
    '--glow-c': 'rgba(16,185,129,0.07)',
    '--glow-d': 'rgba(56,189,248,0.06)',
  },
  cyan: {
    '--accent':        '#38bdf8',
    '--accent-dim':    'rgba(56,189,248,0.12)',
    '--accent-border': 'rgba(56,189,248,0.25)',
    '--accent-glow':   'rgba(56,189,248,0.20)',
    '--wordmark-from': '#38bdf8',
    '--wordmark-to':   '#7dd3fc',
    '--glow-a': 'rgba(56,189,248,0.22)',
    '--glow-b': 'rgba(14,165,233,0.10)',
    '--glow-c': 'rgba(56,189,248,0.05)',
    '--glow-d': 'rgba(56,189,248,0.08)',
  },
  violet: {
    '--accent':        '#a78bfa',
    '--accent-dim':    'rgba(139,92,246,0.12)',
    '--accent-border': 'rgba(139,92,246,0.25)',
    '--accent-glow':   'rgba(139,92,246,0.20)',
    '--wordmark-from': '#a78bfa',
    '--wordmark-to':   '#c4b5fd',
    '--glow-a': 'rgba(139,92,246,0.22)',
    '--glow-b': 'rgba(109,40,217,0.12)',
    '--glow-c': 'rgba(139,92,246,0.05)',
    '--glow-d': 'rgba(167,139,250,0.07)',
  }
};

function setTheme(name) {
  const vars = THEMES[name];
  if (!vars) return;
  Object.entries(vars).forEach(([k, v]) =>
    document.documentElement.style.setProperty(k, v)
  );
  localStorage.setItem('theme', name);
}

// Init on load
setTheme(localStorage.getItem('theme') || 'aurora');
```

---

## Tuning Tips

- **Too intense?** Lower the RGBA opacity values in `--glow-a/b/c/d` by 0.03–0.05.
- **Too subtle?** Increase `--glow-a` toward 0.25. Don't go above 0.30 or it washes out the text.
- **Want more colors?** Add a 5th radial gradient. Place it at an extreme corner (`at 95% 90%`) for a subtle edge bleed.
- **Animated aurora?** Add `@keyframes` that shift `background-position` on the pseudo-element — `background-size: 200% 200%` + `animation: aurora 8s ease infinite alternate`.
- **For light mode?** Flip the base: `--bg: #f8fafc`, reduce glow opacities to 0.06–0.10, use a white surface. The radial gradients become pastel watercolor instead of aurora.
