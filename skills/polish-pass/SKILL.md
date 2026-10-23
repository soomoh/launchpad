---
name: polish-pass
description: Last gate before a design reaches stakeholders or ships — four parallel reviews (accessibility, AI-slop, hierarchy/rhythm, interaction states), then fixes for whatever they turn up. Run it ahead of any handoff, when the user says "polish this", "is this ready to ship", "review before I send it", or when hierarchy or spacing feels off, or interaction states need checking. Also holds the hierarchy/rhythm and interaction-states checklists.
---

# Polish Pass — end-of-design quality gate

**Polished and unpolished designs can share one idea; what separates them is the
care put into execution, and viewers see exactly that.** This is the umbrella
review, meant as the final gate before handoff.

Thresholds and token scales are kept in
`${CLAUDE_PLUGIN_ROOT}/skills/design/references/a11y.md`, `…/design-tokens.md`, and `…/ai-tells.md`. Read them
ahead of dispatch so you can resolve values on your own.

## Phase 1: Confirm scope

Default to the HTML file the user names or has just completed, then to the
project's main deliverable, and ask when neither is evident. After reading it,
write down three things: the medium (slide / page / mobile / dashboard), the
deployment context (internal / customer-facing / marketing), and any
constraints already stated.

Unfinished work (a broken layout, absent sections, placeholder copy still being
rewritten) is a reason to pause: report that and let the user choose between
polishing now or after the structure stabilizes. A moving target makes both
passes wasted effort.

Read the project's brand doc (`.claude/DESIGN.md`, or whatever name the design gateway's *Step 1* finds) and tokens file when they exist: each review
measures the design against its own brand, so a deliberate brand choice is not a
finding.

## Phase 2: Launch four reviewer agents in parallel

Send one message that launches four `launchpad:reviewer` agents (subagent_type `launchpad:reviewer`),
each limited to this file and handed the paths to the brand doc and the
tokens file. For a small single-file design, reviewing inline is fine.

**Every agent makes one pass and spawns nothing** — agents can't start agents, so
the accessibility lens works through the `launchpad:accessibility-audit`
checklist itself instead of using its fan-out procedure. The `launchpad:reviewer` agent
already reports each finding with confidence and severity; Phase 3 does the
filtering.

1. **Accessibility** — every category in `${CLAUDE_PLUGIN_ROOT}/skills/design/references/a11y.md`: contrast
   (resolve and compute each pair), semantic HTML, keyboard and focus, motion,
   forms, hit targets.
2. **AI tells** — each section of `${CLAUDE_PLUGIN_ROOT}/skills/design/references/ai-tells.md`, the
   words section included, judged against the brand.
3. **Hierarchy and rhythm** — the checklist below.
4. **Interaction states** — the checklist below.

If the user's instructions rule out subagents, run the four lenses inline one after another and say so in one line.

### Checklist: hierarchy and rhythm

**Hierarchy steers the eye, and rhythm makes the design look deliberate.** Together
they separate "intentional" from "AI-generated" more than anything else.

Work through this list on every screen, slide, and major section:

1. **Primary / secondary / tertiary.** Say what the eye lands on first, next, and last. Being unable to name them means the hierarchy has failed.
2. **Size.** Expect headings visibly larger than body text and the primary CTA larger than
   secondary actions. Flag two failures: peers rendered at wildly different sizes
   (inconsistent), and unequal items rendered at matching sizes (flat).
3. **Color.** Saturated brand color for primary actions, neutral for secondary,
   light for de-emphasized ones. Flag a single color everywhere (no signal) and
   minor elements that are the brightest (wrong signal).
4. **Weight.** Heavy headlines, normal-weight body, lighter captions. Flag pages
   that are all-bold and pages that are all-regular.
5. **Position.** In LTR layouts the gaze enters at top-left, so that's where the
   important content belongs. Flag a primary element left in the bottom-right corner.
6. **Density.** Generous spacing says "look here"; tight spacing says
   "supporting." Flag the reverse: key content squeezed while filler gets room.
7. **The 5-second test.** A newcomer glancing for five seconds should be able to
   say where to look and what action to take.

For the document as a whole:

1. **Spacing scale.** Every padding, margin, and gap lands on one scale. Write
   down the scale the file implicitly uses and flag outliers.
2. **Type scale.** Flag arbitrary sizes (`17px`, `23px` in a 16/20/24 design).
3. **Repetition.** Repeated units (cards, list rows, feature blocks) keep
   identical padding, gaps, sizes, and structure. Flag pairs that are almost the same but
   *slightly* off; the choice is identical or clearly distinct, with no middle.
4. **Strategic variation.** Over a long page or deck, an occasional pattern break
   is healthy. Flag sameness throughout (monotonous) as well as constant change
   from one section to the next (chaotic).
5. **Palette discipline.** Budget: 3–5 colors with their tints/shades. Flag 8+
   distinct colors, and flag several almost-identical blues or grays used in
   different spots.
6. **Section structure.** Readers should be able to see where one section ends,
   with a single consistent device. Flag sections that blur together and designs
   that use many different dividers.
7. **Alignment.** Flag elements sitting a few pixels off the grid, where it looks
   like sloppy margins and not a purposeful offset.

### Checklist: interaction states

**Controls that give no feedback on state seem defective** — without a hover
state a button resembles a label, and with the focus ring deleted keyboard users
can't navigate.

First, list every interactive element in the file: buttons (including `role="button"` and
anything with a click handler), links, inputs, toggles, clickable cards or rows,
nav items (tabs, sidebar links, breadcrumbs), and custom widgets (dropdowns,
accordions, modals, popovers).

Then test each element against the interactive-states table in `${CLAUDE_PLUGIN_ROOT}/skills/design/references/a11y.md` and the motion
timing bands in `${CLAUDE_PLUGIN_ROOT}/skills/design/references/design-tokens.md` — default, hover, active, focus,
disabled, loading, plus transitions, `prefers-reduced-motion`, action feedback,
and state visibility. Flag all of it, borderline cases too, and attach a
confidence level instead of quietly discarding a finding.

## Phase 3: Aggregate, deduplicate, prioritize

Wait for the four reports. Then fold overlapping findings together
("focus ring removed" will often arrive from both the accessibility and
interaction-states agents) and sort what remains into three tiers:

1. **Blockers** — accessibility failures: contrast below the minimum, missing
   keyboard support, removed focus rings, missing labels. Real users hit a broken
   design. Fix all of them.
2. **Quality issues** — AI-slop tropes, broken hierarchy, missing interaction
   states. They make the design feel cheap. Fix all of them.
3. **Polish recommendations** — smaller refinements, such as nudging a color's tone
   or tightening the spacing scale. Make them if they're within scope; otherwise
   just flag them.

The agents collect evidence; **you make the call.** When a fix isn't obvious,
resolve the underlying values yourself before accepting the finding, and never
read an agent's confidence estimate as a verdict.

## Phase 4: Fix and re-verify

Resolve every blocker and quality issue yourself. If several fixes are plausible
(Inter is in use and the brand names no font), choose the most defensible and
state your choice so the user can override. Clear false positives get logged, not
acted on.

Next, probe where fixes are likely to clash. Has a contrast change dulled a brand
color? Are new focus rings crowding adjacent elements? Is the primary CTA still
the obvious primary? Fixes interfere with one another, so check rather than
assume.

When a fix changes behavior rather than looks, **run it** instead of
reasoning about it.

## Phase 5: Final summary

Keep the report short; the user can ask for more:

- **Verdict** — "Ready to ship" / "Ready after user reviews flagged decisions" /
  "Needs more iteration before polish makes sense"
- **Blockers fixed and polish applied** — a tally for each category
- **Open decisions** — choices the user must approve (font choice, color tone
  shift, emphasis level)
- **Out of scope** — noticed yet left alone (copy edits, content additions, new
  features)
