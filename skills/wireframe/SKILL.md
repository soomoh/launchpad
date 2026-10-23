---
name: wireframe
description: Make low-fidelity greyscale wireframes or storyboards that probe a flow, layout, navigation pattern, or information hierarchy ahead of any hi-fi commitment. Use when the user asks to "explore options", "sketch something out", or "show me a few directions", or when the brief is open-ended enough that hi-fi effort would be wasted. Yields 3+ throwaway variations along a stated axis.
---

# Wireframe — explore many ideas quickly

Probe a flow, layout, or idea before any hi-fi design is committed.
**Wireframes are throwaway.** What they offer is range, not polish in any single one.

## Phase 1: Understand the goal

Confirm five things with the user before drawing. **The subject**: one of a screen, flow, navigation pattern, information hierarchy, or interaction model. **What the user is trying to do** there. **Constraints**: mobile or desktop, existing
context or greenfield, elements that can't change. **Number of variations**: 3 at
the least, 5–6 as the cap per round. **Axis of variation**: layout, density, step
count, or CTA placement.

Given only "wireframe a sign-up flow," suggest 2–3 axes ("single-page form vs.
multi-step wizard vs. progressive disclosure") and ask which to pursue.

## Phase 2: Establish wireframe conventions

Adopt the standard wireframe look so viewers take these as wireframes and not as broken hi-fi:

- **Greyscale only** — no brand color; just black, white, and 2–3 grays
- **System sans-serif** — no typographic character, so the user doesn't start
  judging fonts yet
- **Content areas are boxes with labels** like "headline", "image", "feature card"
- **Imagery is a striped placeholder** with a monospace label
  (`product shot 1200×800`); real pictures are off limits because they steal focus
- **Ipsum or skeleton copy** — save final wording for later
- **Annotations welcome** — numbered callouts at key decisions

Wireframes are the only place where hand-drawn-looking SVG (rectangles, lines, simple
icons) is fine, because everything shares the same low fidelity.

## Phase 3: Sketch variations

Sketch **3 or more** variations, each differing on the agreed axis. Put
single-screen ones next to each other; give each flow variation its own mini storyboard (3–5 screens each).

For the side-by-side canvas, a plain grid is enough:

```css
.canvas { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 32px; padding: 32px; background: #F5F5F5; }
.cell   { background: #FFF; border: 1px solid #DDD; padding: 24px; }
.cell > figcaption { font: 12px/1.4 ui-monospace, monospace; color: #666;
                     margin-bottom: 12px; text-transform: uppercase; }
```

The variation can come from layout (centered / split-screen / grid), information
density, flow structure (single page / multi-step / progressive disclosure), CTA
placement, or navigation pattern. Sequence from the most conventional to the most novel, since
people choose the interesting option more readily when the safe one sits beside a
riskier one.

**Record what makes each variation structurally different before you sketch it.**
Unspecified variations tend to converge on nearly identical layouts. Make the
differences intentional, and ensure at least one is truly off-distribution.

## Phase 4: Annotate

Give each variation 2–4 annotation points, set beside it instead of in a
separate document, so the variation and its rationale are read together:

```
- Variation 1 (tabbed settings): familiar, but hides what changed
- Variation 2 (one long scrolling page): everything visible, hard to scan
- Variation 3 (search-first settings): fast for experts, empty for newcomers
```

## Phase 5: Capture decisions and hand off

Once the user chooses, record the selected variation (or hybrid), what drew them
to it, what they expressly turned down, and any new constraints that came up.
Together these form the brief that the hi-fi work starts from.

Follow with an offer of `launchpad:make-a-prototype` for a hi-fi interactive build,
`launchpad:make-a-deck` if the wireframes were meant for a presentation, or another low-fi round. **Don't
spend hi-fi polish on the wireframes themselves**; they have done their job.

Report which variations you made, what axis they vary on, the step you suggest
next, and any questions left open.
