---
name: ai-slop-check
description: Detect and fix what makes a design read as generic AI output — the house-style clusters (warm editorial, dark acid-accent, broadsheet, SaaS card kit), template chrome (eyebrow labels, middle-dot meta, numbered markers, arrows, mono captions), default fonts and palettes, untraceable colors, off-scale spacing, scattered motion, and templated copy. Use when output risks looking templated ("looks AI-generated", "remove the slop", "make this feel intentional"), after any greenfield hi-fi build, and as part of polish-pass.
---

# AI slop check

A design that looks like a hundred other generated outputs fails to look like
the user's design. This skill applies the catalogue in
`${CLAUDE_PLUGIN_ROOT}/skills/design/references/ai-tells.md` to a real file and fixes what
it finds. The catalogue owns the list; this file owns the procedure.

## Phase 1: Identify the surface and its brand

Review the file the user named; otherwise files changed this session; if
unclear, ask. Read the project's brand doc (`.claude/DESIGN.md`, or whatever name the design gateway's *Step 1* finds) and tokens file if they
exist — **a tell that the brand chose deliberately is not a finding.**

Read the markup, the styles, and the referenced tokens so you can **resolve
actual values**. A color-traceability rule means nothing if the variables were
never resolved.

## Phase 2: Single pass against the catalogue

Read `ai-tells.md`, then check every section of it — clusters, template
chrome, individual defaults, and words. For the clusters, judge the page as a
whole: one element can be deliberate; the full cluster without a brand reason
is the finding.

Report every detection, including uncertain and low-severity ones, each with
`file:line`, the catalogue entry, and a confidence estimate.

## Phase 3: Fix and summarize

Fix directly, using the brand's tokens — never a new inline value. Where
several fixes are reasonable (which typeface replaces a default), pick the
most defensible one for the subject and **name it** so the user can override;
never make a silent taste decision. If no brand exists and the fix needs one,
stop and route to `launchpad:frontend-aesthetic-direction` rather than swapping one
default for another.

Summarize: findings by catalogue section, fixes applied, and open taste
decisions for the user.
