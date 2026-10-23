---
name: make-a-deck
description: Create a slide presentation in one HTML file, with fixed-size 16:9 slides that letterbox into any viewport, on top of the bundled deck_stage.js shell (scaling, keyboard/tap navigation, slide counter, localStorage position, print-to-PDF). Use when the user wants a deck, presentation, slides, or pitch.
---

# Make a Deck

Produce a presentation as one HTML file whose slides have a fixed size
(1920×1080, 16:9 by default) and letterbox into any viewport. **Never write the
scaling yourself**; the bundled shell does it.

## Phase 1: Discovery

Pin these down ahead of any building. **Audience**: it sets tone and density. **Format**:
aspect ratio plus slide count, where a 10-minute talk runs about 10 slides and a
30-minute one about 20–25. **Tone**: one of formal corporate, casual internal,
marketing-bold, or technical. **Source content**: go through any PRD or existing material first. **Speaker notes**: off unless the user explicitly
asks. **Brand / design system**: always confirm it, and if there is none, run
`launchpad:frontend-aesthetic-direction` before drawing.

A request that is already complete ("make a 5-slide deck for engineering
all-hands from this PRD") needs no questions; just build.

## Phase 2: Plan the layout system

Fix the layout system ahead of every slide and write it as a comment block at
the top of the file. Decks usually need 4–6 layout types: cover/title,
section header (full-bleed color or image), content (headline + chart/image/
list), quote/pull-out, comparison/two-column, closing/CTA. For each, specify the
background treatment, where the headline sits and how big it is, the body content
area, and the footer (page number, brand mark, none).

Use no more than **1–2 background colors**. Section headers may add a third;
nothing past that.

## Phase 3: Build the deck shell

Put `assets/deck_stage.js` (shipped with this skill) beside the deck HTML and
include it. It takes care of scaling and letterboxing, keyboard and tap
navigation, the slide counter, localStorage position, and print-to-PDF.

Chrome styles are injected by the shell itself, so no separate stylesheet exists.

```html
<deck-stage width="1920" height="1080">
  <section data-screen-label="01 Title">…</section>
  <section data-screen-label="02 Problem">…</section>
</deck-stage>
<script src="deck_stage.js"></script>
```

Every slide must be a direct child `<section>` of `<deck-stage>`, each with a
`data-screen-label` so the user can name a slide when commenting. **Number labels
from 1**, matching the counter the user sees.

## Phase 4: Build slide by slide

Work through the slides in order, and **show the user the file after 1–2
slides** rather than polishing 15 privately before revealing anything. For each slide:

- **Type.** Body text must not drop below 24px on a 1920×1080 canvas, and 32px+
  is better; headlines run 60–96px+. (The complete per-medium minimums are in
  `${CLAUDE_PLUGIN_ROOT}/skills/design/references/design-tokens.md`.)
- **Hierarchy.** Give each slide a single main message, with supporting elements
  smaller and quieter.
- **Imagery.** Use the design system's assets, or fall back on honest placeholders (striped
  background, monospace label). No hand-drawn SVG filler.
- **No filler slides.** Slides titled "Why choose us?" or "About this deck" drain
  the audience's attention without payoff, so delete them.
- **Charts.** Show only what matters, and remove columns and data points that
  don't back the slide's point. Anything past a trivial chart goes through the
  `dataviz` skill, with the deck's own tokens overriding its default palette.

Take spacing and color from the design system's tokens; add no new inline values.

## Phase 5: Speaker notes (only if requested)

In the head, include a `<script type="application/json" id="speaker-notes">`
array that has an entry for every slide; write each as a complete spoken script,
not a bullet outline. Slides that have notes can hold less text on screen. The shell shows
them in a panel you toggle by pressing `S`.

## Phase 6: Verify and deliver

**Open the deck in a browser and step through it from first slide to last.**
Check scaling at several viewport sizes, a correctly advancing counter, working
keyboard navigation (arrows, space), no overflow past slide bounds, type at or
above the 24px+ minimum, and passing contrast (`launchpad:accessibility-audit`
for the thorough pass).

Finish with a brief summary of caveats (placeholder imagery still pending), next
steps (real charts to swap in), and decisions awaiting the user's sign-off.
