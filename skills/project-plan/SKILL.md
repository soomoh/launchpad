---
name: project-plan
description: Create or update a project's living plan at .claude/PLAN.md — goal, shape and stack, data and privacy posture, trust boundaries, design status, caveats, decisions, and next steps — and surface the caveats and open decisions before building. Use whenever a new project or app starts (even from a one-line idea), a major feature begins, the direction or scope changes, or the user asks to plan, scope, structure, or "figure out how to build" something. Iterative: re-run to update, never regenerate from scratch.
---

# Project plan — one living document

Loosely defined work still needs a shape. This skill keeps **one** short,
living plan per project instead of a stack of specs, and front-loads the
caveats so they are decided before code depends on them.

The plan lives at **`.claude/PLAN.md`** in the project root. It is a working
document for you and the user, not a deliverable: it stays out of git in a
public repo (see Step 3), and
anything a stranger needs ends up in the README instead.

## When it runs

- **New project or app**, even from a one-line idea → create the plan.
- **Major feature or change of direction** → update the affected sections.
- **Resuming work** in a project that has a plan → read it first; it is the
  memory across sessions.

A small task in an established project gets a three-line plan inline in the
conversation, no file.

## Step 1: Gather, don't interrogate

Infer what you can from the request, the repo, and existing files. **An
existing project often has its plan already, under another name** — `CLAUDE.md`
or `AGENTS.md`, a README, `docs/PRD.md`, `docs/ROADMAP.md`, `.specs/`, an issue
list. Read them first and build `PLAN.md` from them: link rather than copy
anything that is still current, and record contradictions as caveats. Ask only
what changes the build, and ask it once, as concrete options with a
recommendation:

- What it's for and who uses it; what "working" looks like.
- Platform and hard constraints (runtime, hosting, offline, budget).
- **Private or may go public?** A business or personal site is usually
  private; a tool or library may be published. Recommend one; it decides the
  scaffolding below.
- **Privacy posture** — what data exists, how sensitive, what must never leave
  the device or server. Always ask if it isn't obvious; it shapes everything.

Dispatch `launchpad:researcher` agents in parallel for anything unfamiliar (a library's
maintenance and licence, an API's limits, how comparable tools are built)
while you draft. Check the actual runtime versions before naming a stack.

## Step 2: Write `.claude/PLAN.md`

Keep it scannable — bullets over prose, a screen or two at most. Sections:

1. **Goal** — one or two sentences, then non-goals.
2. **Shape** — architecture in a paragraph (name the paradigm: local-first,
   client-server, CLI, static site…), the stack with a *why* per choice, and
   the directory layout. Prefer the user's stated stack defaults (their
   CLAUDE.md), if any, unless a reason overrides them. Every runtime
   dependency gets a one-line justification.
3. **Data & privacy** — what is stored, where, and its sensitivity; the hard
   rule for what never leaves; what must never be committed (real data,
   personal config). This drives the `.gitignore`.
4. **Trust boundaries** — where untrusted input enters (HTTP, files, webhooks,
   external APIs, LLM output). Any non-trivial boundary → run `launchpad:threat-model`
   and link its table here rather than restating it. No boundaries → say so.
5. **Design** — brand status: none yet (the `launchpad:design` gateway establishes it on
   the first UI work), or a pointer to `.claude/DESIGN.md` and the tokens file.
6. **Caveats & risks** — the point of the exercise. What could invalidate the
   plan, what is harder than it looks, what the user may not expect (cost,
   licensing, platform limits, data loss on schema change). Ranked.
7. **Decisions** — one line each: decision, alternatives, why. These stop
   future sessions re-litigating settled questions.
8. **Open questions** — decisions that are the user's, with a recommendation.
9. **Next steps** — phased, each phase a usable increment that ends green
   (tests + a real run). Tag tasks by tier where delegation pays:
   `[researcher]`, `[implementer]`, `[tester]`, or Tier 0 tooling; default is
   inline.

## Step 3: Scaffold safety before code (new repos only)

Before the first source file:

- `.gitignore` from `references/gitignore.template`, trimmed to the stack, plus
  the project's own data paths from section 3. For a **private** repo, replace
  its local-notes block with `.claude/settings.local.json`, so Claude's notes
  are committed and backed up.
- `.env.example` with placeholder values for any configuration.
- `LICENSE` — MIT for a public repo unless the user says otherwise; none for a
  private one.
- A README stub: what it is, quickstart — filled in as the project grows.
- Once a remote exists: `git remote set-head origin -a` (or
  `git remote set-head origin <default-branch>` offline). A clone sets
  `origin/HEAD` itself; a remote added to an existing repo does not, and
  diff-against-base tools such as `security-review` fail without it.

Once the stack exists and something runs, write the project's `CLAUDE.md`:
commands, architecture that spans files, invariants, and pointers to
`.claude/PLAN.md` and the brand docs — under ~100 lines, never restating the
user's global rules. It is gitignored in a public repo and committed in a
private one; either way,
anything a person setting the project up needs (setup, commands, how to
contribute) goes in the README too. Keep both current when commands or
structure change.

Commit nothing; committing waits for the user.

## Step 4: Surface, then build

Reply with the **top caveats and the open questions** — not the whole plan —
and proceed with the parts that don't depend on the answers. Point to the plan
file for the rest.

## Updating

On every later run: edit in place. Move answered questions into Decisions,
strike completed steps, add new caveats at the right rank. Never regenerate a
plan that already exists — its decisions are history worth keeping.
