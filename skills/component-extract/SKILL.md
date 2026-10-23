---
name: component-extract
description: Go through a finished design or flow, find the reusable components within it, and output a component inventory (atoms, molecules, organisms, templates) covering variants, states, tokens used, composition, and accessibility notes. Use when the user wants to "make it a system", "build a component library", "identify reusable parts", or give a developer structured pieces.
---

# Component Extract

Find the reusable components in a design and produce an inventory the user can
build a component library from.

**A page is just components arranged.** Pulling them out converts a heap of
one-offs into something you can maintain.

## Phase 1: Identify the surface

Decide the scope: one design file, a multi-page flow, or an entire project. Read
every relevant file and form a picture of the visual vocabulary in play before you
name anything.

## Phase 2: Walk the design and inventory

Take each visual element in turn, section by section, and test it with four questions:

1. Is this precise pattern repeated anywhere?
2. Might it plausibly be used elsewhere? (A card style, form input, or header
   probably recurs even if it sits in one spot now.)
3. Does it come in variants? (Button: primary/secondary/ghost. Card: with/without
   image.)
4. Does it have states? (Hover, active, disabled, focus, loading.)

One yes is enough to make it a component candidate. Then file each candidate under the usual categories:

- **Foundational** — the tokens for color, spacing, type, radius, shadow, and motion (run `launchpad:design-system-extract` for token-level detail)
- **Atoms** — the basics: button, input, checkbox/radio/toggle, select, tag/chip/badge,
  avatar, icon (sizes + set in use), link
- **Molecules** — combinations such as form field (label + input + helper + error), card,
  toast/alert, modal, dropdown menu, tooltip, pagination
- **Organisms** — larger sections like header/nav, footer, sidebar, tab group, table, form, hero,
  feature grid, empty state
- **Templates** — page layouts: landing, detail, list/index, empty-state page

## Phase 3: Document each component

- **Name** — brief, in the usual convention: `Button`, `FormField`
- **Purpose** — when to use it, in one sentence
- **Variants** and **sizes**
- **States** — the ones that apply; the state table is in
  `${CLAUDE_PLUGIN_ROOT}/skills/design/references/a11y.md`
- **Tokens used** — the color, spacing, and type tokens it depends on
- **Composition** — the parts it is made from, e.g. `Card` uses `Button`
- **Accessibility notes** — keyboard support, ARIA, contrast
- **Do / Don't** — a minimum of one each, for instance "Don't put a destructive action in the primary button style"

## Phase 4: Identify the gaps

Include these in the deliverable, since they are the work that stands between a
design and a genuine system:

- **Inconsistencies** — several close-but-different button styles where a single
  one suffices; recommend a canonical version
- **Missing states** — hover defined but focus absent, or nothing for disabled
- **Missing variants** — the design has delete actions but no destructive button variant
- **Off-scale values** — any spacing or size not on the established scale; snap each one onto the scale

## Phase 5: Emit and hand off

Store the inventory in `component-inventory.md`, giving each component its own
section laid out as above, ready to pass to a developer. You may
also render a component-library page that shows every component with its variants
and states, reusing the canvas grid snippet from `launchpad:generate-variations`.

Possible next steps: run `launchpad:design-system-extract` for tokens if it
hasn't been done, implement the library as real code, apply `launchpad:polish-pass`
to the components, or add `launchpad:make-tweakable` to the library. End by
reporting how many components fall in each category, which inconsistencies and
gaps you flagged, where the output lives, and the step you recommend.
