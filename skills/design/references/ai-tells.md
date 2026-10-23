# AI tells — the catalogue

The single owner of "what makes a design read as generated". The `launchpad:design`
gateway reads this at write time to steer away; `launchpad:ai-slop-check` and
`launchpad:polish-pass` read it at review time to detect. Skills cite this file; they
never restate the list.

**Every entry is legitimate for some brief.** A tell is a choice made by
default rather than for this subject. If the brief or the project's brand asks
for it, it isn't a tell — follow the brief. If an axis was left free, don't
spend that freedom here.

Each entry: the default to reach for, then what to detect.

## Whole-look clusters

These are the house styles current models drift into. One element can be
deliberate; the full cluster without a brand reason is the tell.

1. **Warm editorial** — cream background (around `#F4F1EA`), high-contrast
   serif display, italic word-accents, terracotta or clay accent (around
   `#D97757`, which is also Claude's own interface accent). *Default instead:*
   a direction chosen from the subject (`launchpad:frontend-aesthetic-direction`).
2. **Dark terminal-chic** — near-black background with one bright acid-green,
   lime, or vermilion accent, often with monospace everywhere.
3. **Broadsheet** — hairline rules, zero radius, dense newspaper columns,
   small-caps labels, as a look applied to content that isn't editorial.
4. **SaaS card kit** — content chopped into identical rounded cards, one
   radius on everything regardless of hierarchy, the same soft grey shadow
   (`rgba(0,0,0,.1)`) under each, gradient washes as decoration, a
   `border-radius: 12px` + `border-left: 4px` "callout" card used as the
   default card.
5. **Purple-to-pink gradients** — the previous generation's default:
   saturated multi-stop gradients on heroes, buttons, or large surfaces.

## Template chrome

Small devices that appear whatever the subject:

- A tracked-out ALL-CAPS eyebrow label above every heading; all caps for
  labels generally.
- Meta strings joined with middle dots (`Design · Build · Ship`) and labels
  built as `WORD — fragment` with a spaced em dash.
- Numbered markers (`01 / 02 / 03`) on content that is not actually a
  sequence. Use numbers only for real steps, timelines, or rankings.
- A `→` appended to every link and button.
- A monospace face for small data labels and captions as decoration.
- Accenting one word in a headline with italic, bold, or a different color.
- Tinted near-black (`#0B0B0B`, `#111`) standing in for a considered dark.
- The hero as a big number with a small label, supporting stats, and a
  gradient accent.

## Individual defaults

- **Gradients** — *default:* flat color from the system, or a subtle on-tone
  two-stop. *Detect:* 3+ stops, rainbow blends, overlays that don't improve
  legibility.
- **Emoji** — *default:* none, unless the brand uses them or they carry
  meaning (status, category). *Detect:* emoji prefixing headings, buttons, or
  bullets for color.
- **Imagery** — *default:* real photography, professional illustration, an
  established icon set, or an honest placeholder (striped box, monospace size
  label). *Detect:* hand-drawn SVG of people, scenes, or concepts presented as
  final art.
- **Type** — *default:* a family chosen for the subject's tone and medium.
  *Detect:* Inter, Roboto, Arial, Fraunces, Playfair Display, or a bare system
  stack used without a reason. Don't swap one generic for another.
- **Whites and blacks** — *default:* toned to the palette. *Detect:* exact
  `#FFFFFF` with exact `#000000`.
- **Color traceability** — *default:* every color traces to a token. *Detect:*
  five slightly different blues; colors invented inline; framework default
  palettes (Tailwind's grays and semantic hues) used verbatim as a brand.
- **Spacing and size** — *default:* the project's scales. *Detect:* off-scale
  values (`padding: 7px 15px`, `font-size: 17px`).
- **Motion** — *default:* motion that answers a person's action, plus at most
  one orchestrated moment (a page-load sequence or one reveal). *Detect:*
  fade-and-slide-up on every section, hover lift on every card, scattered
  effects with no purpose.

## Words

Copy reads as templated as quickly as layout does.

- **Default:** plain words from the user's side — "Notifications", not
  "Webhook config". Buttons say what happens ("Save changes", not "Submit"),
  and an action keeps its name through the flow ("Publish" → "Published").
  Errors say what happened and how to fix it, in the product's voice, without
  apology. Empty states invite the next action. Sentence case.
- **Detect:** "Learn more" with no destination, "Unlock the power of…",
  "Seamless", "Supercharge", stacked headline + subhead + paragraph that say
  one thing, invented stats, apologetic or vague errors ("Oops! Something went
  wrong"), Title Case On Every Label.
