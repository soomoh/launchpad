---
name: accessibility-audit
description: Audit a design or UI file for accessibility — contrast ratios, semantic HTML, keyboard navigation and focus, motion preferences, form labelling, and hit-target size — and fix the problems found. Use whenever accessibility comes up ("run an accessibility check", "is this WCAG compliant", "keyboard nav") and in any pre-ship review. Fans out to parallel review agents, then applies fixes automatically. Invoked by polish-pass.
---

# Accessibility Audit

Review a design for accessibility problems and fix them. **Accessibility and good design are the same thing** — the payoff reaches keyboard users, people with disabilities, and anyone on a slow network, in bright sunlight, or on an aging device.

Every threshold, checklist, and fallback value is kept in
`${CLAUDE_PLUGIN_ROOT}/skills/design/references/a11y.md`. **Read it first**; this skill
covers the procedure and leaves the numbers to that file. If
`launchpad:polish-pass` is running on this design, skip this skill: the
polish pass already includes the full accessibility review.

## Phase 1: Identify the surface

Start with the HTML file the user just edited or named. If there isn't one, take the design file touched most recently, and if that's ambiguous, ask. Read the whole file, then note the
framework, the target level (WCAG AA unless told otherwise), and any constraints
the user gave.

## Phase 2: Launch four reviewer agents in parallel

From the main session, send one message that launches four `launchpad:reviewer` agents (subagent_type
`launchpad:reviewer`), each given the file path and a pointer to the
a11y reference. The `launchpad:reviewer` agent reports every finding, borderline ones
too, with confidence and severity; aggregation does the filtering.

**Already inside an agent, or auditing one file under 150 lines?** Agents can't start agents,
so cover the four categories below yourself in a single pass.

1. **Contrast and color** — resolve each color pair you can and compute its real
   ratio against the required minimum; color-only signaling; difficult
   combinations (hard to read or colorblind-hostile); pure white-on-black (a style finding, not WCAG).
2. **Semantic HTML and structure** — heading hierarchy, the right element for
   each role, alt text, form labels, ARIA discipline.
3. **Keyboard navigation and focus** — reachability, tab order, interaction
   patterns (Escape, Enter/Space, arrows), visible focus rings, skip links.
4. **Motion, forms, and misc** — `prefers-reduced-motion`, flashing, how specific
   errors are and how they're tied to fields, required-field marking, input types
   and `autocomplete`, hit-target size.

If the user's instructions rule out subagents, run the four lenses inline one after another and say so in one line.

## Phase 3: Aggregate and fix

Hold until all four have reported. Merge the four reports into one list without duplicates, then fix every entry. Fix borderline cases as well — accessibility is
the floor, not the ceiling. Record and skip clear false positives and findings
that are truly out of scope (a third-party embed you can't modify).

The verifier collects evidence; **you make the call.** If a fix isn't obvious,
resolve the underlying value yourself instead of taking an agent's verdict.

## Phase 4: Re-check the high-risk seams

Fixes can undo each other. Check whether recoloring for contrast dulled the brand palette, whether added focus rings crowd nearby elements, and whether replacing an element disturbed the layout. Repair what looks wrong; flag anything you're unsure of.

Close with a summary: count of issues per category (contrast / semantic / keyboard / motion-forms), how many were fixed, and what is left for the user.
