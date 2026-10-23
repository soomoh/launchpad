---
name: design-system-extract
description: Pull design tokens — color, typography, spacing, radii, shadow — out of a brand reference, existing codebase, live site, or screenshots, and write them to a structured tokens file (tokens.css, tokens.ts, tokens.json, or a Tailwind config extension). Use when the user says "extract tokens", "give me a tokens file", "match our existing design", or when new design work has to fit an existing visual language. Called by the design gateway when a brand or codebase already exists.
---

# Design System Extract

Read design tokens from a source and write them to a structured tokens file. Reach
for this when new work must match a visual language that already exists. With the
tokens in place, later designs cite them, so the system stays consistent and the
user isn't asked for values again.

The token categories and the standard scale shapes are in
`${CLAUDE_PLUGIN_ROOT}/skills/design/references/design-tokens.md`. This skill records what
actually *exists*; that reference shows what a complete set looks like.

## Phase 1: Identify sources

Possible sources: a codebase (read the theme files: `theme.ts`, `tokens.css`,
`_variables.scss`, `tailwind.config.js`, design system source), a live site or
screenshots, a brand guide (PDF, Figma, doc), or an existing UI kit.

**If no source is given, ask — made-up tokens defeat the purpose.**

## Phase 2: Extract by category

Record the values the source actually contains. **Never guess**; a token set with
three honest gaps is better than one with three invented values.

- **Colors** — brand primary and accent (plus variants where defined); status colors (success, warning, error, info, along with their light backgrounds); the
  neutral scale (typically 9–11 steps, with its tone noted — warm/cool/neutral);
  and surfaces: background, foreground, card, overlay, border. Record each one's
  value, the name the source gives it, and its documented usage.
- **Typography** — families with complete fallback stacks; the size scale really
  in use, not a generic one; only the weights that are actually loaded; line
  heights; letter spacing where it counts; named text styles ("Heading 1", "Body
  Large") if the source defines any.
- **Spacing** — the scale really in use. A source with distinct scales for inset / inline / block / between-components needs each of them recorded.
- **Radii and shadows** — corner radii (typically 3–5 distinct values) and the
  elevation scale written as full CSS values (offset, blur, spread, color,
  opacity).
- **Other, if present** — z-index layers, animation timings and easings, breakpoints, container widths.

**Flag inconsistencies; never resolve them quietly.** Several slightly different
blues, or neutrals on different tones, go to the user as findings — the
inconsistency tells you something about the source.

## Phase 3: Emit the tokens file

Write `tokens.css`, or **follow the source's format and naming convention**
(`tokens.ts` with typed exports, `tokens.json`, a Tailwind config extension) — a
file the project can adopt as is beats one in the format you'd pick. Organize by
category and use clear names:

```css
:root {
  /* Brand */
  --color-primary: …;   --color-accent: …;
  /* Semantic */
  --color-success: …;   --color-error: …;
  /* Neutrals */
  --color-gray-50: …;   /* … through --color-gray-900 */
  /* Surfaces */
  --color-bg: …;   --color-surface: …;   --color-border: …;

  --font-sans: "…", -apple-system, sans-serif;
  --text-base: 16px;       /* the whole size scale, as it exists in the source */
  --weight-regular: 400;   /* loaded weights only */
  --leading-normal: 1.5;

  --space-1: 4px;          /* the whole spacing scale, as it exists in the source */
  --radius-md: 8px;
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

## Phase 4: Document findings

After that, write or update `.claude/DESIGN.md` following the `launchpad:design` gateway's *Step 1*,
pointing at the tokens file instead of copying its values, so later screens and
sessions build on the same system.

Summarize: **sources used**; **categories extracted**; **gaps** — token sets the source never defines (the user's call; never fill them in quietly);
**inconsistencies** — values that nearly duplicate each other, or sit off the scale, and could be merged; **recommended next steps** — normally a walkthrough of the file with the user, followed by citing it in future designs.
