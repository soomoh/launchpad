---
name: retrospective
description: Review how a substantial session went: which checkpoints fired, which reviews found real problems, where work was redone, and what the user caught that reviews missed. Turn each lesson into a project-notes update or a proposed workflow change. Use when a plan phase completes, before the user starts a fresh session after substantial work, or when the user asks for a retro, a post-mortem, or "what should we change about how we work".
---

# Retrospective

A short look back at the session, so the next one is faster and catches more.
Keep it short: the verdict and the notes are the whole output.

## 1. Gather

Use the session's own record, not memory of how it felt:

- **Checkpoints:** which fired, which were skipped, and whether a skip cost
  anything.
- **Reviews:** each review's findings, split into real ones (fixed) and noise
  (rejected on verification). Note any reviewer whose findings were all noise.
- **Rework:** retries, reverted edits, test-debug loops, files recovered
  from git, and their causes.
- **Misses:** problems the user caught that tests and reviews didn't, and
  why nothing caught them.
- **Cost:** if a usage tool is available (for example `get_usage` in the
  Claude desktop app), read the context size and plan-window use. Note any
  expensive step that changed nothing.

## 2. Classify every lesson, act on the first two kinds

| Kind | Where it goes |
|---|---|
| **Project-specific**: a command, gotcha, or invariant of this codebase | The project's notes (`CLAUDE.md` or the plan). Apply it directly. |
| **Recurs in every project and gives a clear gain** in speed, accuracy, or token use | A proposed change to the Launchpad plugin or the user's global instructions, written as a note with the exact text and where it goes. The user applies it in that repo. |
| **Edge case or minor polish** | Drop it. |

When proposing a workflow change, edit or add as few lines as possible. Never
restructure what fires skills and agents (the checkpoint table, the review
gate, the delegation rules); add to them or sharpen them.

## 3. Report

1. **Verdict:** what worked, what cost tokens for little return, and what to
   change. Three or four lines.
2. **Applied:** the project-notes edits you made.
3. **Proposed:** each workflow change as a short note: the problem seen this
   session, the exact text, and the file and section it goes in.
