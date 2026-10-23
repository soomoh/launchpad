---
name: make-tweakable
description: Attach a floating control panel to a finished design so the user can change it live (colors, fonts, density, layout variants, copy, feature flags) with choices saved to localStorage. Use when the user asks to "play with options", "see different versions", or "make this adjustable", or wants to compare visual choices without regenerating the file.
---

# Make Tweakable

Attach a floating control panel to a finished design so the user can change chosen
aspects live. **Many variants, one file**; never scatter v1.html / v2.html / v3.html.

## Phase 1: Identify what should be tweakable

Agree with the user, or put forward a set for their approval, on what to expose: color (primary, accent, background tone), typography (family, base size,
scale ratio), density (tight / normal / loose), layout variant, component
variants (filled/ghost buttons, card treatment), copy (headline, subhead, CTA),
feature flags (show/hide sections).

**Hold the tweak surface to 3–8 controls.** Offer a handful of meaningful axes,
not a Figma clone. When the user never requested tweaks but the design plainly
has axes worth varying, include 1–2 by default to reveal interesting options.

## Phase 2: Design the panel

Float the panel over the design, usually at bottom-right, semi-transparent with a
subtle border and titled **"Tweaks"**. Match the control to the value type: color
picker for colors; dropdown or button group for fonts and variants; slider with
sensible min/max for numbers; toggle for booleans; text input for copy. A narrow stacked column is better than a wide, sprawling panel.

Provide a visible show/hide toggle. **A hidden panel must be entirely gone**,
neither dimmed nor shrunk into a corner. Any edit-mode chrome left showing makes
the design look unfinished, which defeats the purpose of reviewing it.

## Phase 3: Wire up live updates and persistence

Route visual tokens through CSS custom properties so everything that uses them
changes together:

```js
document.documentElement.style.setProperty('--tweak-primary', newColor);
```

Values outside CSS (copy, layout variants, feature flags) call for JS state with
a re-render, or direct DOM changes.

**Save every tweak to `localStorage` and restore it on load.** Users reload
constantly while iterating on a design, and values lost on reload make it feel broken.

```js
const TWEAK_DEFAULTS = { primaryColor: '#3B82F6', fontSize: 16, dark: false };
const tweaks = { ...TWEAK_DEFAULTS, ...JSON.parse(localStorage.getItem('tweaks') ?? '{}') };
const save = () => localStorage.setItem('tweaks', JSON.stringify(tweaks));
```

Offer a "Reset to defaults" control, so that returning to the baseline after
exploring never requires clearing site data.

## Phase 4: Verify and summarize

Open the file in a browser. Switch the panel on and off; alter each tweak and
check that it applies live; reload and check the values survive; reset and check
the baseline returns; confirm the design looks finished with the panel hidden.
**Execute it rather than reasoning that the wiring is right.**

Close by reporting the exposed tweaks and their value types, the defaults, the
tweaks you considered and dropped (and why), and whether the set covers what the
user wants to explore.
