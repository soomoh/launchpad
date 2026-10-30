# Security

## Reporting a vulnerability

Report privately through the repository's **Security** tab →
**Report a vulnerability**. Please don't open a public issue: Launchpad's
hooks run on users' machines, and a public report exposes them before a fix
exists.

## In scope

- Getting a secret or a private term past the commit guard
  (`scripts/commit_guard.py`).
- A hook or script running a command, or reading or writing a file, that it
  shouldn't.
- Anything that sends data off the user's machine.
- `setup` changing a user's settings without their confirmation.

Out of scope: bugs in Claude Code itself (report those to Anthropic), and
behaviour a user enabled in their own settings.

## What to expect

Launchpad is a personal project maintained on a best-effort basis. Fixes go
into the latest version only.
