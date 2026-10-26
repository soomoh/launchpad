---
name: frontend-aesthetic-direction
description: Establish a project's brand from nothing — commit to a concrete, subject-grounded aesthetic direction (typography, color, density, radius/shadow, component style, imagery, motion, voice), check it against the brief for generic defaults, and record it as a tokens file plus .claude/DESIGN.md brand guidelines. Use before any greenfield hi-fi work, when the user says "no brand yet", "pick a look", "define the brand", "what should this feel like", or when designs keep drifting generic. Invoked by the design gateway when no brand exists.
---

# Frontend aesthetic direction — a brand from nothing

Mocking hi-fi from scratch without a committed direction is the fastest path
to template output. Commit first, prove it small, then record it so every
later screen builds from the same system.

Concrete scales, palette construction, and font candidates live in
`${CLAUDE_PLUGIN_ROOT}/skills/design/references/design-tokens.md`; the generic defaults to
steer away from live in `…/references/ai-tells.md`. Read both before
proposing anything.

## Phase 1: Confirm it's really greenfield

No brand guide, existing product, reference site, or partial theme in the
repo. If any exists, stop and use `launchpad:design-system-extract` instead — extracting
beats inventing.

## Phase 2: Ground it in the subject

Establish, asking only what you can't infer: the **subject** and its world
(materials, vernacular, artefacts, the people in it); the **audience**;
**three adjectives** for the feel; **references** the user admires and what
specifically about them; **off-limits** looks.

The subject is the source of distinctiveness. A brief for a ceramics studio, a
tax tool, and a kids' game should produce directions that could not be
swapped between them.

## Phase 3: Propose, then check against the brief

If the user hasn't fixed a direction, propose **four** — each concrete
(background and accent hex, display + body typeface, layout idea in a
sentence, one-line rationale tied to the subject). They must not share a
palette family, and at least one should be deliberately off-distribution.

**Before showing them, review each against the brief.** Ask: would I have
produced this for any similar brief? Compare against the clusters in
`ai-tells.md`. Anything that reads as a default rather than a choice for *this*
subject gets revised — say what you changed and why. A cluster from
`ai-tells.md` is acceptable only when the brief genuinely calls for it, and
then the direction says so explicitly.

## Phase 4: Commit on every axis

Vague statements ("modern and clean") produce generic designs. Commit:

- **Typography** — specific families (1–2), weights, a type scale, line
  lengths; a free alternative for any paid foundry.
- **Color** — tone (warm, cool, neutral); primary with light/dark variants; at
  most one accent; semantic colors and a 5–10 step neutral scale **derived on
  that tone** (`oklch()`), not copied from a framework palette.
- **Density** — tight, normal, or loose.
- **Radius and shadow** — one identity; shadows tinted from the palette.
- **Component style** — filled, ghost, outlined, or elevated, with a default.
- **Imagery and iconography** — photography, illustration, an icon set, or
  honest placeholders; never hand-drawn SVG art.
- **Motion** — quiet, expressive, or playful; at most one orchestrated moment.
- **Voice** — how the product writes: tone, vocabulary, and how errors and
  empty states speak.

## Phase 5: Prove it small

Build one small surface — a hero, a card, a button group with all states — in
the direction, run `launchpad:ai-slop-check` on it, then show it. Ask whether
it reads as the three adjectives. A direction that fails small gets worse at
scale; revise before going broader.

## Phase 6: Record the brand

Write the two files the `launchpad:design` gateway defines (its *Step 1* lists the
`.claude/DESIGN.md` sections):

- **The tokens file** in the stack's format, with a short header comment
  naming the direction.
- **`.claude/DESIGN.md`** — principles and adjectives, committed choices per axis,
  light/dark with measured contrast, the components built so far with their
  states, voice, and open decisions.

From here on, every design references these tokens. A new value goes into the
tokens file and `.claude/DESIGN.md` first, then into the design.

Summarize: the three adjectives, the committed choice per axis, what you
revised during the brief check and why, and any axis the user should confirm.
