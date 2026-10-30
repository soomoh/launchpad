---
name: quality-audit
description: Whole-codebase audit against the standard of a well-run open-source project — correctness, security, privacy, maintainability, tests, and publish-readiness, including a scan of the full git history for secrets and personal data. Works with or without a git remote. Use before a project is called done, shared, or published; when the user asks "is this ready", "audit this", "is this good enough to open source", or for a code-quality or security review of the whole codebase rather than a diff. Fans out parallel reviewer agents, then verifies and ranks their findings.
---

# Quality audit — would a stranger trust this repo?

The bar: a repository you would be comfortable publishing today. Diff-level
review (the review gate in Launchpad's session guidance) catches what changed; this catches
what accumulated — including what is buried in history.

## Phase 1: Ground truth (inline, before any agent)

Run things; don't infer them. Record the real output.

1. **Inventory** — stack, size (`git ls-files | wc -l`), entry points, test
   command, CI config, lockfile(s), licence, README.
2. **The project's own checks** — its format, lint, and test commands exactly
   as CI or the README defines them. A red suite is a finding by itself.
   **If the user didn't write this repo, look before running:** read the
   package scripts (install/postinstall/test), test setup and config files,
   and git hooks first; install with lifecycle scripts off
   (`npm ci --ignore-scripts`); run the checks only inside the sandbox — never
   via commands the user's settings exempt from it, such as browser tests —
   and ask before anything that would leave it. Tooling that would act
   outside the project when run (network calls, files beyond the repo, shell
   out to the system) is a finding in its own right.
3. **Secrets and personal data in history** —
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/commit_guard.py" --history <repo>`. Every hit is a
   blocker: deleting the line later does not unpublish it.
4. **What `git add .` would take** — `git status --porcelain` for untracked,
   unignored files; anything personal or generated there means the
   `.gitignore` is not doing its job.
5. **Remote base branch** — with a remote, `git symbolic-ref
   refs/remotes/origin/HEAD` must resolve; if it doesn't, set it
   (`git remote set-head origin -a`) so base-branch diffs and
   `security-review` work.
6. **Dependency advisories** — the native audit per
   `${CLAUDE_PLUGIN_ROOT}/skills/security/references/supply-chain.md` (needs network; say
   so if unavailable).

## Phase 2: Fan out reviewers

Dispatch `launchpad:reviewer` agents **in one message**, one lens each, each given the
repo path, the Phase 1 facts, its checklist below, and the reference files it
should read. Scale to the codebase: under ~2,000 lines, combine lenses into two
or three agents; a tiny repo can be reviewed inline.
If the user's instructions rule out subagents, run the lenses inline one
after another and say so in one line.

1. **Correctness & robustness** — logic bugs, unhandled failure paths,
   swallowed errors, skip-vs-stop confusion, sentinel/zero conflation, input
   not normalized at the boundary, crashes on a user's mistake.
2. **Security** — `${CLAUDE_PLUGIN_ROOT}/skills/security/SKILL.md` red flags, then
   its `references/owasp-patterns.md` (and `llm-security.md` if an LLM is called):
   injection, missing authorization, XSS, SSRF, unsafe deserialization, path
   traversal, secrets in code, headers and CORS, rate limits — and the
   project's own tooling: install scripts, test setup, and hooks that act
   outside the repo when run.
3. **Privacy** — personal data in code, fixtures, logs, error messages, or
   telemetry; data leaving the device without a named reason; real data where
   synthetic fixtures belong; absolute personal paths.
4. **Maintainability** — the design vocabulary in
   `${CLAUDE_PLUGIN_ROOT}/skills/engineering/SKILL.md`: hand-rolled solved
   problems, if/elif chains that should be data, unclear names, comments that
   say what instead of why, speculative abstraction. Then ask what can be
   deleted: dead code, commented-out code, unused options and config keys,
   paths a replacement superseded, and dependencies, services, or build steps
   without a stated reason.
5. **Tests** — logic tested at the seam; the catastrophic failure mode pinned
   explicitly; risky paths with no test; mocks where fixture files belong;
   fixtures that look like real data.
6. **Publish readiness**, judged against the intended audience (ask if it
   isn't clear; assume public when unsure) — README the intended reader can
   follow (run the quickstart mentally against the repo), one authoritative
   lockfile, `.gitignore` in safety-device shape, no TODO-shaped
   placeholders. CI, where it exists, runs the local commands, fails on lint
   warnings, has read-only `permissions`, and SHA-pins third-party actions.
   If a released version exists, changes since then to the plan's stable
   surface come with upgrade notes. **Public:** a LICENSE; a `SECURITY.md`
   giving a private way to report a vulnerability (GitHub private reporting
   is enough); Claude's notes not tracked unless a contributor needs them
   (`git ls-files .claude CLAUDE.md AGENTS.md`). **Private:** no licence
   needed, and the hosted repo actually private.

If the project has a UI, also run `launchpad:polish-pass` on its main surfaces.

## Phase 3: Verify and judge (you, not the agents)

For every finding, open the cited lines and confirm the failure scenario
yourself before accepting it. Merge duplicates across lenses. Discard false
positives, but say how many and why in one line.

Rank what survives:

1. **Blockers** — secrets or personal data anywhere in history, exploitable
   security issues, data leaving the boundary, failing checks, missing licence.
2. **Should fix before publishing** — correctness bugs, untested risky paths,
   README that doesn't work, unjustified dependencies.
3. **Polish** — maintainability and style improvements.

## Phase 4: Report

Write the full report to `.claude/AUDIT.md` (gitignored) and reply with the
short version:

- **Verdict** — "Ready to publish", "Ready after the blockers", or "Not yet".
- **Blockers**, each with `file:line` and the failure in one line.
- Counts for the other two tiers, with the top three of each.
- What was not checked and why (no network for the dependency audit, no
  browser for the UI).

## Fixing

Fix nothing unless the user asks. When they do, take blockers first, add a
regression test for each bug, and re-run Phase 1 checks after.

**Secrets in history need the user, not a rewrite.** The order is: revoke and
rotate the credential first, then — only with explicit approval — purge it
from history (`git filter-repo`), knowing that rewritten history breaks every
existing clone.
