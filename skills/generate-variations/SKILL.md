---
name: generate-variations
description: Deliver 3+ truly different hi-fi design variations of a screen, component, or flow, running from conventional to bold and differing in layout, hierarchy, interaction model, and tone, all in one file with captions and a recommended pick. Use when the user wants options, alternatives, "different takes", or "show me a few" for hi-fi work.
---

# Generate Variations

Give the user several distinct designs so they can lift the best parts of each.
**Variations are the cheapest route to good design**: a single design is a single
gamble, while three let the user throw out what misses and merge what lands.

## Phase 1: Establish the baseline

Settle four things first. **The subject**: a screen, component, flow, or visual
treatment, since its scope sets how many variations make sense. **Design
context**: anchor variations in the UI kit or design system unless told to depart
from it. **Count**: 3 by default, with 5–6 as a sensible cap. **Axis
preference**: visuals, interactions, layout, or copy/tone, meaning where the
exploration should concentrate.

## Phase 2: Pick the axes

Choose 2–4 dimensions to flex: visual treatment (color tone, density, shadow,
radius, type weight); layout (centered vs. asymmetric, single vs. multi-column,
full-bleed vs. inset); interaction model (single page vs. multi-step, modal vs.
inline); information hierarchy; tone; component style. **Record the axis each
variation moves on**, so the user can compare them at a glance.

## Phase 3: Build with intent — basic to bold

Sequence them from the most conventional to the most unusual:

1. **By the book.** Follows the established patterns and conventions; the safe choice.
2. **Refined.** Keeps the structure but pushes one or two dimensions: heavier
   type, a more assured layout, livelier color. Frequently what the user ends up choosing.
3. **Novel.** A truly different approach: an unorthodox layout, a bold visual
   metaphor, a daring look. It widens the discussion and exposes tastes the user
   hadn't realized they had.
4. **4–6 (if requested).** Hybrids drawn from the range, or an out-of-left-field option on another axis.

**Span the full range.** A set of only safe options wastes the user's time; a set of only wild ones disregards the brief.

## Phase 4: Vary substantively, not cosmetically

Real differences live in layout, hierarchy, what leads, type system, density,
interaction approach, or copy strategy, **not** merely in button color, accent
shade, or shadow opacity. When two look alike, replace one with something more
substantial. Any pair should be distinguishable by the user in a single sentence.

**Pin down every variation in concrete terms before building it**: its own
palette family, its own type pairing, its own layout skeleton, noted per
variation. Variety has to be planned rather than hoped for, because unspecified
variations slide toward a single default look (usually the warm-editorial house
style). For the novel one, intentionally choose something outside the usual
distribution that still interests.

## Phase 5: Present in a single file

**Never output v1.html / v2.html / v3.html.** Use one file in which every
variation is visible or switchable. Static variations go on a canvas grid:

```css
.canvas { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
          gap: 40px; padding: 40px; background: var(--color-bg); }
.cell   { background: var(--color-surface); border: 1px solid var(--color-border); }
.cell > figcaption { font: 12px/1.5 ui-monospace, monospace; padding: 12px 16px;
                     border-bottom: 1px solid var(--color-border); }
```

When the variations share a structure and differ along only a few axes, use
`launchpad:make-tweakable` instead of the canvas grid, so the user can switch between them live. For flows, make each variation a miniature storyboard placed in the canvas.

## Phase 6: Annotate and recommend

Write one or two sentences under each variation, like "Variation 2 — Refined. Same
structure, expressive headline type, warmer palette." **Captions double as a
test**: a variation you can't caption clearly isn't distinct enough.

End on a firm recommendation. The decision belongs to the user, but a designer
still takes a position ("Variation 2 is my pick — the safety of 1 with more visual
confidence"). Never claim the options are equally good, because they aren't.

Finish by proposing what comes next: refine the chosen direction, run another
round on a different axis, go interactive with `launchpad:make-a-prototype`, or
move to `launchpad:polish-pass` if the user is ready to ship.
