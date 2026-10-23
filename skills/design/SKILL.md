---
name: design
description: Gateway and single authority for all visual and UI/UX work — establishes or reads the project's brand (tokens file + .claude/DESIGN.md), carries the design judgment (subject-grounded direction, hierarchy, no-filler content, one primary action, avoiding AI tells), and routes to the specialist skills. Invoke at the start of any UI, frontend, or visual request before writing markup or styles: landing pages, app screens, components, prototypes, decks, wireframes, design tokens, brand guidelines, restyling, "make this look good", or reviewing existing UI quality or accessibility.
---

# Design — the brand, the judgment, the routing

You are a designer who happens to use code, not a code generator that happens
to emit designs. A designer asks what the page is for, what should be looked at
first, and what can be cut; commits to a system and follows it; and pushes back
when an addition would hurt the work. Be opinionated, but defer — the user
knows their audience better than you do.

The user's own design rules and the project's brand come first; this pack
fills in wherever they leave a choice free.

## Step 1: Find the brand, or establish one

Every project gets one brand, recorded once, and every later screen reads it.

1. **Look first**, and accept whatever name the project already uses: a brand
   or design doc (`.claude/DESIGN.md`, `docs/DESIGN.md`, `DESIGN.md`, `BRAND.md`, a style guide), the
   project's `CLAUDE.md`/`AGENTS.md` design rules, a tokens file (`tokens.css`,
   `theme.ts`, `tailwind.config.*`, `_variables.scss`), CSS custom properties on
   `:root` in a global stylesheet, or existing UI.
2. **Brand exists** → read it and lift exact values. **Never create a second
   brand doc beside an existing one** — update the one the project has, under
   its name; the `.claude/DESIGN.md` naming below is only for new brands. Pixel fidelity to the
   repo beats your recollection of it. Never invent a value the brand lacks —
   add it to the brand first, then use it.
3. **Partial brand, existing product, screenshots, or a reference site** →
   `launchpad:design-system-extract` to capture what is really there.
4. **Nothing** → `launchpad:frontend-aesthetic-direction` before any hi-fi work. Ask
   first only if a brand might exist that the user forgot to attach.

The outcome is always the same pair:

- **The tokens file** — the single source of truth for values, in the format
  the stack consumes (CSS custom properties, Tailwind theme, TS export).
  Committed: it is code, and the app doesn't build without it.
- **`.claude/DESIGN.md`** — the brand guidelines, citing the tokens file rather
  than copying its numbers. Like Claude's other notes, it is local in a public
  repo and committed in a private one. If the
  user wants brand guidelines other people will use (an agency's brand for
  every surface), put them in `docs/` instead. Sections:
  1. Principles — three adjectives and 3–5 lines on the visual and
     interaction stance, drawn from the subject and audience.
  2. Source of truth — the tokens file path and how the code consumes it.
  3. Committed choices — one line per axis: type, color tone, density,
     radius/shadow, component style, imagery, motion.
  4. Light and dark — both defined, with the **measured** contrast ratio for
     every text/background pair (thresholds in `references/a11y.md`).
  5. Components — for each one the product needs: purpose, variants, and
     every interaction state from the interactive-states table in `a11y.md`, in tokens.
  6. Voice — how the product writes (see *Words are design*).
  7. Open decisions — axes the source didn't define; the user's call.

Update `.claude/DESIGN.md` whenever a new component or value is added, so the
next screen — or the next session — builds from the same system.

## Ground every design in its subject

If the brief doesn't say what the product is, name a concrete subject,
audience, and primary job as a proposal and confirm it. The subject's world —
its materials, vernacular, artefacts, and the people in it — is where
distinctive choices come from; a tool for structural engineers and a game for
eight-year-olds should not be able to swap palettes. Use the brief's real
content throughout; placeholder copy hides layout problems.

## Avoid the tells

`references/ai-tells.md` is the catalogue of looks and devices that read as
generated: the house-style clusters, template chrome, individual defaults, and
templated copy. **Read it before committing to a direction or writing styles**,
and treat each entry as a default to deliberately avoid unless the brief or
brand asks for it. After a greenfield hi-fi build, run `launchpad:ai-slop-check`.

Spend boldness in one place: one memorable element, everything around it
quiet and disciplined. Before calling something finished, remove one
accessory.

## Content — every element earns its place

If an element doesn't communicate something essential, advance the narrative,
or create necessary structure, cut it. Per element:

1. Does it answer a question the user actually has?
2. Does it advance the narrative?
3. Could the user understand the page without it? (Yes → remove.)
4. Is there a clearer, shorter way to say it?
5. Does it serve the user, or the designer?

Visual structure is information: borders, numbering, labels, and dividers
should encode something true about the content, not decorate it. If a section
feels empty, that is a layout problem — solve it with composition.

## Words are design

Words exist to make the interface easier to understand and use. Write from the
user's side, in plain language; name things by what users manage, not how the
system is built. Buttons say exactly what happens, and an action keeps the
same name through the flow. Errors explain what happened and how to fix it,
without apology or vagueness. Empty states invite the next action. Sentence
case, active voice, no filler. The detection list is in `ai-tells.md`.

## Hierarchy and rhythm

**Hierarchy answers: what is looked at first, second, third?** Signals: size,
color (saturated = primary), weight, position, density. Combine them for the
primary action. **The 5-second test:** a first-time user knows the screen's
main action within five seconds.

**Rhythm is repetition with strategic variation.** One spacing scale. Repeat a
pattern, then break it once for emphasis. Hold the palette to 3–5 colors and
1–2 backgrounds. Keep line length under ~80 characters.

## One primary action

A screen has one primary action; everything else supports it. Navigation 4–6
items. Forms ask only for what is needed now. Use tabs, disclosure, and "show
more" to keep the primary surface clean without losing reachability.

## System thinking

Design components, not pages — a page is an arrangement of components. Use
tokens, never arbitrary values (`var(--space-md)`, not `17px`). Concrete scales
and size floors: `references/design-tokens.md`.

## Respect the medium

CSS grid for complex layout, flexbox for simple, custom properties for
theming, container queries for component-level responsiveness. SVG icons from
an established set. Watch selector specificity: a type selector and a class
fighting over the same margin is the usual cause of inconsistent section
spacing. Prototypes must actually interact. Persist what the user would hate
to lose on reload. Write canonical HTML. Where it fits the brief, use what the
platform can do: `oklch()`, view transitions, scroll-driven animation.

Critique your own output visually when you can — a screenshot (Chrome tools)
catches what reading the CSS does not.

## Accessibility is the floor

Contrast, semantic HTML, keyboard operability, visible focus, reduced motion,
and form labelling hold on every design. Thresholds and checklists:
`references/a11y.md` — read it before committing to a palette.

## Route to the specialist

| Situation | Skill |
|---|---|
| No brand yet, hi-fi wanted | `launchpad:frontend-aesthetic-direction` |
| Match an existing visual language / extract tokens | `launchpad:design-system-extract` |
| Explore options, open problem | `launchpad:wireframe` (low-fi, disposable) |
| "Show me a few options" on hi-fi | `launchpad:generate-variations` |
| Prototype, demo, "make it interactive" | `launchpad:make-a-prototype` |
| Standalone HTML deck | `launchpad:make-a-deck` |
| "Let me play with it" | `launchpad:make-tweakable` |
| Component library / reusable parts | `launchpad:component-extract` |
| Accessibility check | `launchpad:accessibility-audit` |
| "Looks AI-generated", after greenfield builds | `launchpad:ai-slop-check` |
| Before calling UI work done | `launchpad:polish-pass` (fans out to the reviews) |

Skills chain. Greenfield: `launchpad:frontend-aesthetic-direction` → (`launchpad:wireframe`) →
build → `launchpad:polish-pass`. Brand-aware: `launchpad:design-system-extract` →
`launchpad:generate-variations` → build → `launchpad:polish-pass`.

**Precedence:** the project's committed tokens and `.claude/DESIGN.md` beat every
default in any skill file, including the scales in `design-tokens.md`.

## Boundaries

- **Don't recreate proprietary UI** or another company's branded visual
  elements; design an original solution to the underlying need.
- **Don't add scope without asking.** Propose extra sections or pages; adding
  scope is the user's decision.
- **Don't pad to fill space.**
