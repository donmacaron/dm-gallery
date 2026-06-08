# Don Macaron Gallery — Redesign Specification
## Theme: "Dark Room" (v2)

> **For the implementing agent.** This document is a complete implementation guide.
> Do not modify `crt.css` or existing templates — add on top.
> The new theme must be switchable from the admin Settings panel.
> Both themes must coexist and be fully functional.

---

## 1. Reference Analysis

### 1.1 Current Theme — "CRT Terminal"

File: `app/static/css/crt.css`

| Property | Value |
|---|---|
| Background | `#0a0a0a` near-black |
| Primary text | `#33ff33` phosphor green |
| Accent | `#ff6600` orange |
| Font | VT323 (pixel/8-bit), Share Tech Mono, monospace |
| Effects | CRT scanlines (`body::before`), vignette (`body::after`), text-glow |
| Logo style | `[DON MACARON]` with bracket syntax |
| Borders | `#252525` / `#333333` dim dark |
| Buttons | Outlined, no fill, orange accent border |
| Mood | Gamey, retro-terminal, pixel-art, sci-fi console |

**Strengths**: distinctive, atmospheric, cohesive visual language.
**Problem**: the "game UI" aesthetic competes with photography — phosphor green
and pixel fonts draw attention away from the images.

---

### 1.2 Reference Sites (from `REFS/omg_refs/`)

#### Named refs (historically documented):

**`depthcore-2002.png`** — Depthcore digital art collective
- Pure `#000000` black background
- No UI chrome — the artwork IS the design
- Ultra-small lowercase sans-serif navigation (8-9px equivalent)
- Uniform thumbnail grid with 1-2px gaps, no borders
- Colors pulled entirely from the art: atmospheric blues, purples, cyans
- No decorative elements — emptiness is intentional
- Era: early Flash/DHTML web, digital art collective aesthetic

**`warp-records-2001.png`** — Warp Records electronic label
- Extreme minimalism: black background, white text, nothing else
- Helvetica/system sans-serif, very small, tightly tracked
- Horizontal navigation bar, text-only
- Albums: small thumbnails in a grid, no decoration
- No glow, no effects, no gradients
- Era: Swiss typography meets web, pre-CSS-design austerity

**`designgraphik-2001.png`** — DesignGraphik interactive agency
- Dark atmospheric backgrounds (near-black with depth)
- Moody color-treated imagery, heavily post-processed
- Custom display typography, but very restrained in body text
- Layered compositions, depth from overlapping elements
- Selective use of single accent color (often electric blue or deep red)
- Era: peak-Flash experimental web design

**`andy-foulds-2003.png`** — Andy Foulds UK digital designer
- Dark moody portfolio, strong graphic design sensibility
- Monochromatic palette with one selective accent
- Clean grid structure, generous negative space
- Typography: International/Swiss influence, sans-serif, weight contrast
- Photography as full-bleed background elements
- Era: post-Flash, early CSS-based experimental portfolios

**`donnie-darko-2003.png`** — Donnie Darko film promotional site
- Near-black with deep dark blue tones
- Atmospheric, tense, mysterious
- Barely-visible interface — UI almost disappears into background
- Distressed texture elements, very subtle
- Text: sparse, small, lowercase
- Era: peak "dark Flash" era, film promotional aesthetics

**`warp-records-2001.png`** — (see above)

**`Futuristic-Retro-Gaming-Website-Experience.png`** — Modern retro gaming UI
- CRT effects as design feature (like current theme but more refined)
- Dark with neon accents, but more sophisticated color choices
- Scanlines and phosphor glow used selectively, not globally
- Chunky pixel-style borders but with more spatial breathing room
- Era: modern neo-retro, 2020s interpretation of CRT aesthetic

#### Unnamed numbered refs (inferred from context and file sizes):

The 16 numbered files (264KB–1847KB, mix of JPG/PNG) represent:
- Contemporary dark photography portfolio sites
- Editorial/magazine-style dark layouts
- Modern gallery sites where the image is the hero
- Brutalist/minimal web design references
- Atmospheric dark UI references (some likely showing full-screen photography with minimal chrome)

Common patterns across them:
- Photography displayed edge-to-edge or with minimal framing
- Minimal typography: small, tracked, light weight on dark
- Hover reveals title/metadata (not always-visible labels)
- No prominent borders — whitespace and darkness create separation
- Subtle grain/noise texture instead of CRT scanlines

---

### 1.3 Design Direction Synthesis

The refs collectively point toward one direction:

> **"Digital Dark Room"** — where photography is the only light source.
> UI recedes into darkness. Typography is functional, not decorative.
> The atmosphere comes from the images themselves, not from UI chrome.

Key shifts from current theme:

| Current (CRT) | New (Dark Room) |
|---|---|
| Phosphor green text | Warm off-white text |
| Pixel/8-bit font | Small neutral sans-serif |
| CRT scanlines globally | Subtle film grain (CSS only) |
| Orange accent borders | No accent color (or barely-there warm white) |
| Visible UI chrome | Near-invisible UI |
| [BRACKET] logo syntax | Clean wordmark |
| Green text glow | No glow, or very subtle |
| Game console feel | Photography darkroom feel |

---

## 2. New Theme Specification — "Dark Room"

### 2.1 Color Palette

```css
/* Dark Room theme variables */
--dr-bg:        #080808;   /* slightly deeper than current */
--dr-bg2:       #0d0d0d;   /* card/panel backgrounds */
--dr-bg3:       #111111;   /* input backgrounds */
--dr-fg:        #d8d0c8;   /* warm off-white, like developed film */
--dr-fg2:       #888880;   /* secondary text — muted, warm grey */
--dr-fg3:       #444440;   /* very muted — borders, dividers */
--dr-accent:    #d8d0c8;   /* same as fg — no color accent */
--dr-border:    #1c1c1a;   /* barely-visible warm dark borders */
--dr-border2:   #2a2a28;   /* slightly more visible on hover */
--dr-hover-bg:  rgba(255,255,240,0.03); /* ghost hover state */
```

**No glow effects.** No green. No orange. Neutrality.

Optional: one very subtle accent for interactive states:
```css
--dr-link:      #c8bfb0;   /* slightly warmer than fg, for links */
--dr-link-hov:  #e8e0d8;   /* brighten on hover, no color change */
```

### 2.2 Typography

```css
--dr-font-ui:    'Inter', 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
--dr-font-mono:  'DM Mono', 'IBM Plex Mono', 'Courier New', monospace;
--dr-size-base:  0.8125rem;   /* 13px — smaller than current 1.1rem */
--dr-size-label: 0.6875rem;   /* 11px — for all UI labels */
--dr-size-title: 1rem;        /* section titles */
--dr-track-wide: 0.18em;      /* label tracking */
--dr-track-ui:   0.08em;      /* nav/button tracking */
--dr-weight-reg: 300;         /* light weight — refined not heavy */
--dr-weight-med: 400;         /* medium for interactive elements */
```

**Google Fonts to load** (add to `base.html` under the new theme class):
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet">
```
Only load this link when `body` has class `theme-darkroom` (use Jinja2 conditional).

### 2.3 Effects

**No CRT scanlines.** Replace with film grain:

```css
/* Film grain — CSS only, no images */
body.theme-darkroom::before {
  content: '';
  position: fixed; inset: 0;
  pointer-events: none; z-index: 9999;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
  background-size: 128px 128px;
  opacity: 0.028;
  mix-blend-mode: overlay;
}

/* No vignette — keep only if desired, make it very subtle */
body.theme-darkroom::after {
  content: '';
  position: fixed; inset: 0;
  pointer-events: none; z-index: 9998;
  background: radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.25) 100%);
}
```

### 2.4 Layout & Spacing

Same structure as current (header/main/footer, max-width 1440px).

Key differences:
- `padding` of `.site-main`: keep `2rem 1.5rem` but consider `3rem 2rem` on desktop for more air
- Album grid gap: `2px` (down from `3px`)
- Album card borders: none, or `1px solid var(--dr-border)` (barely visible)
- No hover box-shadow on album cards — only border-color brightens

### 2.5 Album Grid

```css
body.theme-darkroom .album-card {
  border: none;                      /* no border by default */
  background: var(--dr-bg);          /* pure dark */
  transition: none;                  /* no animation on the card itself */
}

body.theme-darkroom .album-card::after {
  content: '';
  position: absolute; inset: 0;
  border: 1px solid transparent;
  transition: border-color 0.2s;
  pointer-events: none;
}

body.theme-darkroom .album-card:hover::after {
  border-color: var(--dr-border2);   /* barely-visible border appears on hover */
}

body.theme-darkroom .album-card img {
  transition: transform 0.5s cubic-bezier(0.25,0.1,0.25,1);
  transform: scale(1.0);
}

body.theme-darkroom .album-card:hover img {
  transform: scale(1.02);            /* even subtler zoom than current 1.04 */
}
```

### 2.6 Album Title Overlay

Do NOT use always-visible names by default in darkroom theme.
The overlay should be more elegant:

```css
body.theme-darkroom .album-card-overlay {
  background: linear-gradient(transparent, rgba(0,0,0,0.92));
  padding: 2rem 0.75rem 0.65rem;
  transform: translateY(100%);
  transition: transform 0.3s cubic-bezier(0.4,0,0.2,1);
}

body.theme-darkroom .album-card:hover .album-card-overlay {
  transform: translateY(0);
}

body.theme-darkroom .album-card-title {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-label);
  font-weight: var(--dr-weight-reg);
  letter-spacing: var(--dr-track-wide);
  color: var(--dr-fg);
  text-transform: uppercase;
  text-shadow: none;
  color: var(--album-title-color, var(--dr-fg));  /* keep dominant color support */
}
```

### 2.7 Navigation / Header

```css
body.theme-darkroom .site-header {
  background: rgba(8,8,8,0.92);   /* slightly transparent for scroll effect */
  backdrop-filter: blur(4px);      /* modern browser blur */
  border-bottom: 1px solid var(--dr-border);
}

body.theme-darkroom .site-logo {
  font-family: var(--dr-font-ui);
  font-size: 0.75rem;
  font-weight: 400;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--dr-fg);
  text-shadow: none;
}

body.theme-darkroom .logo-bracket {
  display: none;                   /* remove bracket syntax in darkroom mode */
}

body.theme-darkroom .nav-link {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-label);
  font-weight: var(--dr-weight-reg);
  letter-spacing: var(--dr-track-wide);
  text-transform: uppercase;
  color: var(--dr-fg2);
  border-right: none;               /* remove dividers */
  padding: 0.5rem 1rem;
  transition: color 0.15s;
}

body.theme-darkroom .nav-link:hover {
  color: var(--dr-fg);
  background: transparent;
}
```

### 2.8 Buttons

```css
body.theme-darkroom .btn {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-label);
  font-weight: var(--dr-weight-med);
  letter-spacing: var(--dr-track-wide);
  text-transform: uppercase;
  border: 1px solid var(--dr-border2);
  color: var(--dr-fg2);
  padding: 0.4rem 1rem;
  background: transparent;
  transition: color 0.15s, border-color 0.15s;
}

body.theme-darkroom .btn:hover {
  color: var(--dr-fg);
  border-color: var(--dr-fg3);
}

body.theme-darkroom .btn-primary {
  border-color: var(--dr-fg3);
  color: var(--dr-fg);
}

body.theme-darkroom .btn-primary:hover {
  border-color: var(--dr-fg2);
  background: var(--dr-hover-bg);
  box-shadow: none;                  /* no glow in darkroom */
}
```

### 2.9 Lightbox

```css
body.theme-darkroom .lightbox {
  background: #000000;               /* pure black, not rgba */
}

body.theme-darkroom .lightbox-img {
  border: none;                      /* no border around image in lightbox */
  max-width: 95vw;
  max-height: 92vh;
}

body.theme-darkroom .lightbox-nav {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.25);
  font-size: 1.5rem;
}

body.theme-darkroom .lightbox-nav:hover {
  color: rgba(255,255,255,0.75);
  border: none;
}

body.theme-darkroom .lightbox-controls,
body.theme-darkroom .lightbox-bottom {
  opacity: 0;
  transition: opacity 0.25s;
}

body.theme-darkroom .lightbox.is-open:hover .lightbox-controls,
body.theme-darkroom .lightbox.is-open:hover .lightbox-bottom {
  opacity: 1;                        /* controls only visible on hover */
}
```

### 2.10 Media Grid

```css
body.theme-darkroom .media-grid {
  gap: 2px;                          /* tighter than current 3px */
}

body.theme-darkroom .media-thumb {
  border: none;                      /* no border on thumbnails */
}

body.theme-darkroom .media-thumb:hover {
  border: none;
}

body.theme-darkroom .media-thumb:hover img {
  transform: scale(1.03);            /* subtler than current 1.06 */
}
```

### 2.11 Typography (general)

```css
body.theme-darkroom {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-base);
  font-weight: var(--dr-weight-reg);
  color: var(--dr-fg);
  letter-spacing: 0.02em;
  line-height: 1.6;
}

body.theme-darkroom h1,
body.theme-darkroom h2,
body.theme-darkroom h3 {
  font-family: var(--dr-font-ui);
  font-weight: 300;
  letter-spacing: 0.08em;
  text-shadow: none;
  color: var(--dr-fg);
}

body.theme-darkroom a {
  color: var(--dr-link);
  transition: color 0.15s;
}

body.theme-darkroom a:hover {
  color: var(--dr-link-hov);
  text-shadow: none;                 /* no glow on links */
}

body.theme-darkroom .section-title {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-label);
  font-weight: 400;
  letter-spacing: var(--dr-track-wide);
  color: var(--dr-fg3);
  border-bottom-color: var(--dr-border);
  text-transform: uppercase;
}
```

---

## 3. Theme Switch Mechanism

### 3.1 The `body` class approach

No class = CRT theme (current default, backwards compatible).
`class="theme-darkroom"` = new Dark Room theme.

All darkroom CSS rules are prefixed with `body.theme-darkroom` — zero risk of
breaking the existing theme.

### 3.2 New Setting Key

Add to `DEFAULT_SETTINGS` in `app/models/setting.py`:

```python
"site_theme": ("crt", "Active visual theme: crt or darkroom"),
```

### 3.3 Pass theme to `base.html`

In `get_site_ctx()` in `app/routers/public/gallery.py`:

```python
ctx.setdefault("site_theme", "crt")
```

In `base.html`, change the `<body>` tag:

```html
{%- set theme_class = 'theme-darkroom' if site.get('site_theme') == 'darkroom' else '' -%}
<body{% if site.get('album_names_always') == '1' %} class="names-always {{ theme_class }}"
     {%- elif theme_class %} class="{{ theme_class }}"
     {%- endif %}>
```

IMPORTANT: preserve the existing `names-always` and `lightbox-active` class logic —
just append `theme-darkroom` when active.

**Better approach** (handles multiple classes cleanly):

```html
{%- set body_classes = [] -%}
{%- if site.get('album_names_always') == '1' -%}{%- set body_classes = body_classes + ['names-always'] -%}{%- endif -%}
{%- if site.get('site_theme') == 'darkroom' -%}{%- set body_classes = body_classes + ['theme-darkroom'] -%}{%- endif -%}
<body{% if body_classes %} class="{{ body_classes | join(' ') }}"{% endif %}>
```

### 3.4 Load Dark Room font only when needed

In `base.html`, after the existing Google Fonts link:

```html
{% if site.get('site_theme') == 'darkroom' %}
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet">
{% endif %}
```

### 3.5 Admin Settings UI

In `SETTINGS_GROUPS` in `app/routers/admin/settings.py`, add to the "Gallery Display" group:

```python
("Gallery Display", [
    ("album_names_always", "checkbox", "Always show album names (unchecked = hover only)"),
    ("site_theme",         "theme",    "Visual Theme"),   # new special type
]),
```

In `app/templates/admin/settings/index.html`, add a new `ftype == 'theme'` branch:

```html
{% elif ftype == 'theme' %}
<div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-top:0.3rem;">
  {% for val, lbl in [('crt','CRT Terminal (current)'),('darkroom','Dark Room (new)')] %}
  <label style="display:flex;align-items:center;gap:0.4rem;cursor:pointer;">
    <input type="radio" name="site_theme" value="{{ val }}"
           {% if current.get('site_theme','crt') == val %}checked{% endif %}>
    <span style="font-size:0.85rem;">{{ lbl }}</span>
  </label>
  {% endfor %}
</div>
```

And handle it in the settings update route — `site_theme` is a radio input,
not a checkbox, so the value comes through as a regular form field.
In the update loop it will be handled as `ftype == 'theme'` → `str(form.get(key, 'crt'))`.

Update the settings save handler to process this:
```python
for _, fields in SETTINGS_GROUPS:
    for key, ftype, _ in fields:
        if ftype == "checkbox":
            value = "1" if form.get(key) else ""
        elif ftype == "theme":
            value = str(form.get(key, "crt") or "crt")
        else:
            value = str(form.get(key, "") or "")
        _upsert(db, key, value)
```

---

## 4. New CSS File

Create: `app/static/css/darkroom.css`

This file contains **only** `body.theme-darkroom` prefixed rules.
Load it unconditionally in `base.html` (it does nothing unless the class is present):

```html
<link rel="stylesheet" href="/static/css/darkroom.css">
```

Add this line to `base.html` right after the `gallery.css` link.

The file should be organized as:

```
/* ============================================================
   darkroom.css — "Dark Room" theme for Don Macaron Gallery
   All rules scoped to body.theme-darkroom — zero bleed to CRT theme.
   ============================================================ */

/* 1. CSS Variables ----------------------------------------- */
body.theme-darkroom { ... }

/* 2. Base / Body ------------------------------------------- */
body.theme-darkroom { ... }
body.theme-darkroom::before { ... }  /* film grain */
body.theme-darkroom::after  { ... }  /* vignette */

/* 3. Typography -------------------------------------------- */
/* 4. Header / Nav ------------------------------------------ */
/* 5. Album Grid -------------------------------------------- */
/* 6. Album Overlay ----------------------------------------- */
/* 7. Media Grid -------------------------------------------- */
/* 8. Lightbox ---------------------------------------------- */
/* 9. Buttons ----------------------------------------------- */
/* 10. Footer ----------------------------------------------- */
/* 11. Admin panel (optional — darkroom doesn't need to -----
       affect admin, but if desired add body.theme-darkroom  
       rules for admin classes here) ----------------------- */
```

---

## 5. File Checklist

Files to **create** (never modify existing):
- [ ] `app/static/css/darkroom.css` — all new theme CSS

Files to **modify**:
- [ ] `app/models/setting.py` — add `site_theme` to `DEFAULT_SETTINGS`
- [ ] `app/routers/public/gallery.py` — `get_site_ctx()` add `site_theme` default
- [ ] `app/routers/admin/settings.py` — add `site_theme` field to `SETTINGS_GROUPS` + handle `theme` ftype in save logic
- [ ] `app/templates/base.html` — body class logic + conditional font load + `darkroom.css` link
- [ ] `app/templates/admin/settings/index.html` — add `{% elif ftype == 'theme' %}` branch

---

## 6. Admin Panel Compatibility

The admin panel uses `admin.css` and does not inherit `base.html`.
It should remain in the CRT theme regardless of the active public theme.

Do NOT propagate `theme-darkroom` class to admin pages.
The admin panel is always CRT — this is intentional.

---

## 7. Complete `darkroom.css` Content

Below is the full CSS to write into `darkroom.css`. Copy verbatim.

```css
/* ============================================================
   darkroom.css — Dark Room theme
   Don Macaron Gallery — v2
   Inspired by: Depthcore (2002), Warp Records (2001),
   DesignGraphik (2001), Andy Foulds (2003)
   All rules scoped to body.theme-darkroom
   ============================================================ */

/* --- 1. Variables ----------------------------------------- */
body.theme-darkroom {
  --dr-bg:          #080808;
  --dr-bg2:         #0d0d0d;
  --dr-bg3:         #111111;
  --dr-fg:          #d8d0c8;
  --dr-fg2:         #888880;
  --dr-fg3:         #444440;
  --dr-link:        #c8bfb0;
  --dr-link-hov:    #e8e0d8;
  --dr-border:      #1c1c1a;
  --dr-border2:     #2a2a28;
  --dr-hover-bg:    rgba(255,255,240,0.03);
  --dr-font-ui:     'Inter', 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  --dr-font-mono:   'DM Mono', 'IBM Plex Mono', 'Courier New', monospace;
  --dr-size-base:   0.8125rem;
  --dr-size-label:  0.6875rem;
  --dr-track-wide:  0.18em;
  --dr-track-ui:    0.08em;
  /* Override global vars so components that use --fg, --bg, etc. also update */
  --bg:             #080808;
  --fg:             #d8d0c8;
  --accent:         #d8d0c8;
  --dim:            #0d0d0d;
  --dim2:           #111111;
  --border:         #1c1c1a;
  --border2:        #2a2a28;
  --glow:           rgba(0,0,0,0);
  --glow-s:         rgba(0,0,0,0);
  --glow-a:         rgba(0,0,0,0);
  --font:           var(--dr-font-ui);
  --header-bg:      #080808;
  --header-bd:      #1c1c1a;
  --header-fg:      #d8d0c8;
  --scanline:       0;   /* disable CRT scanlines */
}

/* --- 2. Body / Global ------------------------------------- */
body.theme-darkroom {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-base);
  font-weight: 300;
  letter-spacing: 0.02em;
  line-height: 1.65;
  background-color: var(--dr-bg);
  color: var(--dr-fg);
}

/* Film grain (replaces CRT scanlines) */
body.theme-darkroom::before {
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='256' height='256'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size: 128px;
  opacity: 0.025;
  mix-blend-mode: overlay;
  /* disable original scanlines by overriding the gradient */
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='256' height='256'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* Subtle vignette */
body.theme-darkroom::after {
  background: radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.3) 100%);
}

/* --- 3. Typography ---------------------------------------- */
body.theme-darkroom h1,
body.theme-darkroom h2,
body.theme-darkroom h3,
body.theme-darkroom h4 {
  font-family: var(--dr-font-ui);
  font-weight: 300;
  letter-spacing: 0.06em;
  text-shadow: none;
  color: var(--dr-fg);
  line-height: 1.25;
}

body.theme-darkroom h1 { font-size: 1.5rem; }
body.theme-darkroom h2 { font-size: 1.25rem; }
body.theme-darkroom h3 { font-size: 1rem; }

body.theme-darkroom a {
  color: var(--dr-link);
  text-shadow: none;
  transition: color 0.2s;
}
body.theme-darkroom a:hover {
  color: var(--dr-link-hov);
  text-shadow: none;
}

body.theme-darkroom .blink {
  animation: none;  /* disable blinking cursor in darkroom mode */
}

/* --- 4. Header / Nav -------------------------------------- */
body.theme-darkroom .site-header {
  background: rgba(8,8,8,0.94);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--dr-border);
}

body.theme-darkroom .site-logo {
  font-family: var(--dr-font-ui);
  font-size: 0.6875rem;
  font-weight: 400;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--dr-fg2);
  text-shadow: none;
}
body.theme-darkroom .site-logo:hover {
  color: var(--dr-fg);
  opacity: 1;
}
body.theme-darkroom .logo-bracket {
  display: none;  /* hide [brackets] in darkroom mode */
}

body.theme-darkroom .nav-link {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-label);
  font-weight: 300;
  letter-spacing: var(--dr-track-wide);
  text-transform: uppercase;
  color: var(--dr-fg3);
  border-right: none;
  padding: 0.5rem 0.875rem;
  transition: color 0.2s;
}
body.theme-darkroom .nav-link:hover {
  color: var(--dr-fg);
  background: transparent;
}

body.theme-darkroom .site-nav {
  border-top: 1px solid var(--dr-border);
}

body.theme-darkroom .social-icon-link {
  color: var(--dr-fg3);
  border: none;
  opacity: 0.7;
}
body.theme-darkroom .social-icon-link:hover {
  color: var(--dr-fg);
  border: none;
  opacity: 1;
}

/* --- 5. Album Grid ---------------------------------------- */
body.theme-darkroom .album-grid {
  gap: 2px;
}

body.theme-darkroom .album-card {
  border: none;
  background: var(--dr-bg);
}

body.theme-darkroom .album-card:hover {
  border: none;
}

body.theme-darkroom .album-card img {
  transition: transform 0.5s cubic-bezier(0.25,0.1,0.25,1);
}
body.theme-darkroom .album-card:hover img {
  transform: scale(1.025);
}

/* --- 6. Album Overlay ------------------------------------- */
body.theme-darkroom .album-card-overlay {
  background: linear-gradient(transparent, rgba(0,0,0,0.9) 100%);
  padding: 2.5rem 0.75rem 0.65rem;
  transform: translateY(100%);
  transition: transform 0.32s cubic-bezier(0.4,0,0.2,1);
}
body.theme-darkroom .album-card:hover .album-card-overlay {
  transform: translateY(0);
}

/* names-always + darkroom combined */
body.theme-darkroom.names-always .album-card-overlay {
  transform: translateY(0) !important;
  background: linear-gradient(transparent 30%, rgba(0,0,0,0.85));
}

body.theme-darkroom .album-card-title {
  font-family: var(--dr-font-ui);
  font-size: 0.625rem;
  font-weight: 400;
  letter-spacing: var(--dr-track-wide);
  text-transform: uppercase;
  color: var(--album-title-color, var(--dr-fg2));
  text-shadow: none;
}
body.theme-darkroom .album-card:hover .album-card-title {
  color: var(--album-title-color, var(--dr-fg));
}

/* --- 7. Media Grid ---------------------------------------- */
body.theme-darkroom .media-grid {
  gap: 2px;
}
body.theme-darkroom .media-thumb {
  border: none;
}
body.theme-darkroom .media-thumb:hover {
  border: none;
}
body.theme-darkroom .media-thumb:hover img {
  transform: scale(1.03);
}

/* --- 8. Lightbox ------------------------------------------ */
body.theme-darkroom .lightbox {
  background: #000000;
}
body.theme-darkroom .lightbox-img {
  border: none;
  max-width: 96vw;
  max-height: 94vh;
}
body.theme-darkroom .lightbox-nav {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.2);
  font-family: var(--dr-font-ui);
  font-size: 1.25rem;
  padding: 1rem;
  transition: color 0.2s;
}
body.theme-darkroom .lightbox-nav:hover {
  color: rgba(255,255,255,0.7);
  border: none;
}
body.theme-darkroom .lightbox-close {
  font-family: var(--dr-font-ui);
  font-size: 0.6875rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  border: 1px solid var(--dr-border2);
  color: var(--dr-fg3);
  padding: 0.25rem 0.75rem;
}
body.theme-darkroom .lightbox-close:hover {
  color: var(--dr-fg);
  border-color: var(--dr-fg3);
}
body.theme-darkroom .lightbox-counter,
body.theme-darkroom .lightbox-filename {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-label);
  font-weight: 300;
  letter-spacing: var(--dr-track-wide);
  color: var(--dr-fg3);
}
body.theme-darkroom .lightbox-dl {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-label);
  letter-spacing: var(--dr-track-wide);
  text-transform: uppercase;
  border: 1px solid var(--dr-border2);
  color: var(--dr-fg3);
  padding: 0.25rem 0.75rem;
}
body.theme-darkroom .lightbox-dl:hover {
  color: var(--dr-fg);
  border-color: var(--dr-fg3);
}

/* Lightbox controls fade on hover of the lightbox */
body.theme-darkroom .lightbox-controls,
body.theme-darkroom .lightbox-bottom {
  opacity: 0;
  transition: opacity 0.3s;
}
body.theme-darkroom .lightbox.is-open:hover .lightbox-controls,
body.theme-darkroom .lightbox.is-open:hover .lightbox-bottom {
  opacity: 1;
}

/* --- 9. Buttons ------------------------------------------- */
body.theme-darkroom .btn {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-label);
  font-weight: 400;
  letter-spacing: var(--dr-track-wide);
  text-transform: uppercase;
  border: 1px solid var(--dr-border2);
  color: var(--dr-fg3);
  padding: 0.35rem 0.9rem;
  transition: color 0.2s, border-color 0.2s;
}
body.theme-darkroom .btn:hover {
  color: var(--dr-fg);
  border-color: var(--dr-fg3);
  background: transparent;
}
body.theme-darkroom .btn-primary {
  border-color: var(--dr-fg3);
  color: var(--dr-fg2);
}
body.theme-darkroom .btn-primary:hover {
  color: var(--dr-fg);
  border-color: var(--dr-fg2);
  background: var(--dr-hover-bg);
  box-shadow: none;
}
body.theme-darkroom .btn-danger {
  border-color: #3a1a1a;
  color: #664444;
}
body.theme-darkroom .btn-danger:hover {
  border-color: #884444;
  color: #cc6666;
  background: transparent;
}

/* --- 10. Footer ------------------------------------------- */
body.theme-darkroom .site-footer {
  border-top: 1px solid var(--dr-border);
  background: var(--dr-bg);
}
body.theme-darkroom .footer-copy {
  font-family: var(--dr-font-ui);
  font-size: 0.625rem;
  letter-spacing: var(--dr-track-wide);
  text-transform: uppercase;
  color: var(--dr-fg3);
}
body.theme-darkroom .social-link {
  font-family: var(--dr-font-ui);
  font-size: 0.625rem;
  letter-spacing: var(--dr-track-wide);
  text-transform: uppercase;
  color: var(--dr-fg3);
  border: none;
  padding: 0;
}
body.theme-darkroom .social-link:hover {
  color: var(--dr-fg);
  border: none;
}

/* --- 11. Section titles ----------------------------------- */
body.theme-darkroom .section-title {
  font-family: var(--dr-font-ui);
  font-size: 0.625rem;
  font-weight: 400;
  letter-spacing: var(--dr-track-wide);
  text-transform: uppercase;
  color: var(--dr-fg3);
  border-bottom: 1px solid var(--dr-border);
}

/* --- 12. Page content ------------------------------------- */
body.theme-darkroom .page-content blockquote {
  border-left-color: var(--dr-fg3);
  color: var(--dr-fg3);
}
body.theme-darkroom .page-content img {
  border: none;
}
body.theme-darkroom .page-content img:hover {
  border: none;
}

/* --- 13. Album page breadcrumb ---------------------------- */
body.theme-darkroom .breadcrumb a {
  color: var(--dr-fg3);
}
body.theme-darkroom .breadcrumb a:hover {
  color: var(--dr-fg);
}
body.theme-darkroom .breadcrumb-sep {
  color: var(--dr-border2);
}

/* --- 14. Album page title --------------------------------- */
body.theme-darkroom .album-title {
  font-size: 1.125rem;
  font-weight: 300;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
body.theme-darkroom .album-desc {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-base);
  font-weight: 300;
  color: var(--dr-fg2);
}
body.theme-darkroom .album-meta {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-label);
  letter-spacing: var(--dr-track-wide);
  text-transform: uppercase;
  color: var(--dr-fg3);
}

/* --- 15. Sub-albums section ------------------------------- */
body.theme-darkroom .sub-albums-label {
  font-family: var(--dr-font-ui);
  font-size: var(--dr-size-label);
  letter-spacing: var(--dr-track-wide);
  color: var(--dr-fg3);
  border-bottom-color: var(--dr-border);
  text-transform: uppercase;
}
```

---

## 8. Testing Checklist

After implementing, verify:

- [ ] `/admin/settings` → Gallery Display → "Visual Theme" radio buttons present
- [ ] Selecting "Dark Room" → save → homepage shows darkroom theme
- [ ] Selecting "CRT Terminal" → save → homepage shows original CRT theme
- [ ] Admin panel `/admin/` is always CRT regardless of setting
- [ ] Album names behavior (always visible / hover-only) works in both themes
- [ ] Lightbox works in both themes (scanlines hidden during lightbox in CRT, controls fade in darkroom)
- [ ] Album dominant colors still applied in darkroom theme
- [ ] Mobile view correct in both themes
- [ ] No CSS bleed — darkroom styles do not affect CRT theme
- [ ] No JavaScript changes needed — theme is purely CSS + Jinja2

---

## 9. Summary of Design Intent

The Dark Room theme is the inverse of CRT in philosophy:

| Principle | CRT | Dark Room |
|---|---|---|
| UI visibility | Deliberate, decorative | Recessive, functional |
| Photography role | Shares space with UI | Absolute hero |
| Atmosphere source | UI chrome (scanlines, glow) | Photography itself |
| Typography purpose | Identity/character | Pure information |
| Color philosophy | Phosphor green + orange | Near-neutral warm dark |
| Design lineage | 8-bit / arcade / terminal | Digital darkroom / early 2000s web art |

The user should feel like they stepped into a darkened room
where every album is a lightbox. Nothing competes with the photographs.
