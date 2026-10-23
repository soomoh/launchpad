# Eval results

Launchpad is measured with `claude plugin eval`: each case runs in fresh,
isolated sessions **with** the plugin and **without** it (a no-plugin
baseline), and graders score what Claude produced. Nothing from the author's
own setup loads in either arm.

**Run:** 2026-10-23 · Claude Code 2.1.309 · model under test: Sonnet ·
judge: Haiku · 3 runs per arm per case · total cost about $2.60.

## Does the right skill fire?

| | Runs |
|---|---|
| Trigger cases where the expected skill was invoked | **18 / 18** |
| Quick-question case where no skill fired (correct) | **3 / 3** |

## Does it change the outcome?

Scores are the share of graders passed, averaged over runs. "Skill fired" is
reported separately and not counted in the score, so the two arms stay
comparable.

| Case | What's graded | With | Without | Δ |
|---|---|---|---|---|
| Bug fix | Ships a regression test; doesn't hide "no value" as `0` | **1.00** | 0.33 | +0.67 |
| Plan, answers given | Plan written to a file; risks specific to the app | **1.00** | 0.50 | +0.50 |
| Landing page | Page written; keyboard-visible focus styles (`:focus-visible`) | **1.00** | 0.50 | +0.50 |
| New project idea | Decisions with a recommendation before code; privacy addressed | **1.00** | 0.83 | +0.17 |
| Upload endpoint | Content-checked image, size cap, server-generated filename | 1.00 | 1.00 | 0.00 |
| Quick question | Short correct answer; no skills, no setup pitch | 1.00 | 1.00 | 0.00 |

### Reading the results

- **Where Launchpad adds the most:** habits a capable model skips when not
  told — writing the regression test, persisting the plan, accessibility
  details in UI work, and treating "no value" differently from zero.
- **Where it adds nothing measurable:** Sonnet already hardens a file upload
  well on its own (7 of 8 baseline runs across all runs so far). The security
  skill still fires there; its value is consistency, not this case's score.
- **No cost on simple questions:** the quick question is answered the same
  way with the plugin loaded — no detour into process.

## What the evals changed

The evals found two real gaps, both fixed before this run:

- The security skill didn't fire on "just show me the code" requests (0 of 2
  in the pilot). The guidance now says to load the named skill before the
  work, including for small requests — it fired 3 of 3 afterwards.
- Bug fixes skipped the test when Claude couldn't run code. The engineering
  rule now says to write and show the test anyway — 3 of 3 afterwards, up
  from 1 of 3.

## Caveats

- Three runs per arm is a small sample; treat differences under about 0.3 as
  noise.
- Measured on Sonnet only. Other models may need less or more steering.
- LLM-judged graders can vary between runs; the file and tool-use graders
  don't.
- The cases measure behaviors Launchpad is designed to produce; they are
  evidence that it does what it says, not a general benchmark.

## Reproduce

```bash
claude plugin eval . --runs 3 --model sonnet --allow-tools Write --no-publish
```

Each run uses your own Claude usage. `--no-publish` keeps the report, which
contains full transcripts, on your machine.
