# Design tokens — scales, palettes, and size floors

This file alone owns the concrete visual values. Skills point here and never
repeat the numbers. A project's own tokens **take precedence** — what follows are
defaults for starting from nothing.

## Color

### Building a palette from scratch

Reach for `oklch()` to get harmony: keep lightness and chroma fixed and change
only the hue.

```css
--blue:   oklch(50% 0.15 250);
--teal:   oklch(50% 0.15 200);
--purple: oklch(50% 0.15 280);
```

Hex codes picked at random saturations and brightnesses come out chaotic; this
approach comes out balanced.

**Choose a single tone** — warm (cream, beige, gold, terracotta), cool
(gray, slate, ice, blue), or neutral (concrete, charcoal). A palette that mixes
tones looks arbitrary.

**Keep to 3–5 colors** across the whole product. Past that, no single color reads
as primary.

### Complete palette shape

```css
/* Brand */
--primary: …;  --primary-dark: …;  --primary-light: …;  --accent: …;

/* Semantic — derived on the palette's tone, not a framework's defaults.
   Hue carries the meaning; lightness and chroma match the brand. */
--success: oklch(55% 0.13 150);  --warning: oklch(70% 0.14 75);
--error:   oklch(55% 0.18 25);   --info:    oklch(55% 0.12 245);

/* Neutrals — 10-step scale with a little of the brand hue, so the grays
   belong to this palette (Tailwind's gray-50…900 used verbatim is a tell) */
--gray-50: oklch(98% 0.005 <hue>);  /* … */  --gray-900: oklch(22% 0.01 <hue>);

/* Surfaces */
--color-bg: …;  --color-surface: …;  --color-border: …;
```

### Toned whites and blacks

Don't set pure `#FFFFFF` on `#000000`. Take the palette's tone instead:

| Tone | Background | Text |
|---|---|---|
| Warm | `#FFFAF0` | `#2D2118` |
| Cool | `#F5F7FA` | `#1F2937` |
| Neutral | `#FAFAFA` | `#1A1A1A` |

### Combinations to avoid

Four pairings cause trouble: red beside green (the most common colorblindness), blue beside yellow at close lightness, light gray on white, and colored text on a colored background of close lightness. **Don't let color alone** carry a state — add an icon, text, or
position.

## Typography

**At most 1–2 families.** A sans for body with a serif for headlines works; a
single family throughout works; three or more is chaos. Pair by contrast —
geometric sans against organic serif, light against bold. Pairing two sans-serifs that look alike gains nothing.

### Type scale

```css
--text-xs: 12px;   --text-sm: 14px;   --text-base: 16px;  --text-lg: 18px;
--text-xl: 20px;   --text-2xl: 24px;  --text-3xl: 30px;   --text-4xl: 36px;
--text-5xl: 48px;
```

Stay on the scale. `17px` and `23px` inside a 16/20/24 design look like
mistakes.

### Line height

About 1.1 tight for headlines, about 1.5 normal for body, about 1.7 loose for
long-form. Tracking usually only deserves attention on all-caps labels.

### Font selection

Skip the reflexive defaults — Inter, Roboto, Arial, bare system
stacks, and the serif-display defaults (Fraunces, Playfair Display,
Georgia-as-display). Match the font to the mood you want: humanist sans (Söhne, Suisse), modern serif
(Tiempos, GT Sectra), editorial classic (Tiempos Headline, Canela), typewriter
mono (JetBrains Mono, IBM Plex Mono), geometric sans (Visby). Where a paid foundry could be unaffordable, list a free stand-in (Söhne → Albert Sans or
Geist).

**Body text has to stay readable**: use a sans-serif or a text serif (Georgia,
Merriweather). Reserve cursive, script, and heavy display faces for short labels.
Skip all-caps for blocks of text — reading relies on word shapes, and all-caps erases
them. Add `text-wrap: pretty` so lines don't end in widows or orphans.

### Size floors per medium

These are delivery requirements, not suggestions:

| Medium | Minimum |
|---|---|
| 1920×1080 slides | body never under 24px, ideally 32px+; headlines 60–96px+ |
| Print | never under 12pt |
| Mobile | body never under 16px |
| Desktop | 14–16px body is standard |

Interactive hit targets also have a minimum size — that floor concerns
accessibility and belongs to `a11y.md`.

## Spacing

A single scale, in multiples of 4px or 8px:

```css
--space-xs: 4px;   --space-sm: 8px;   --space-md: 16px;
--space-lg: 24px;  --space-xl: 40px;  --space-2xl: 64px;
```

Values off the scale (`padding: 7px 15px`, `margin: 18px`, `gap: 13px`) look
chaotic. Snap them onto it.

## Radius and shadow

Choose one identity and keep it:

- **Sharp** (0–2px) — utilitarian, brutalist, editorial
- **Soft** (4–8px) — typical modern product
- **Pill / fully rounded** — playful, friendly, consumer

```css
--radius-sm: 4px;  --radius-md: 8px;  --radius-lg: 12px;  --radius-full: 9999px;
--shadow-sm: …;    --shadow-md: 0 4px 12px oklch(30% 0.03 <hue> / 0.12);   --shadow-lg: …;
```

Shadows follow the same split: sharp, soft, or none. **Use a single elevation
system, never a blend.** Tint shadows from the palette; the identical neutral
`rgba(0,0,0,.1)` beneath every card is one of the tells in `ai-tells.md`. Let
radius vary with hierarchy instead of applying one radius to everything.

## Density

Tight (compact dashboards, dense data), normal (typical product UI), or loose
(editorial, marketing, premium). Density is something users feel as much as see —
choose one and apply it throughout.

## Motion

Settle on one mode; a mix feels accidental.

- **Quiet** — transitions on state changes only, 200ms ease
- **Expressive** — entrance animations, scroll-driven reveals
- **Playful** — springs, micro-interactions on hover

Timing: **0.15–0.3s** for state changes (hover, focus, active); **0.3–0.5s** for
entry/exit (modals, drawers, toasts). Anything under 0.15s feels jarring, a
micro-interaction over 0.5s feels laggy, and no transition at all feels broken.

## Other token sets, when the project needs them

Z-index scale, breakpoints, container widths, animation easings. Record these
only when something really does vary along that axis.
