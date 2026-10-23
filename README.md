# Launchpad

A complete development workflow for Claude Code, as one plugin. Install it on a
fresh setup and Claude plans projects before building, applies consistent
engineering standards, routes UI work through a design system, reviews code and
security when a piece of work is finished, delegates to tiered subagents, and
refuses commits that contain secrets.

> Status: in development (v0.1). Full documentation comes with the first release.

## Install

In Claude Code:

```
/plugin install launchpad --marketplace soomoh/launchpad
```

Then run `/launchpad:setup` once. It checks your existing setup for conflicts
and offers recommended safety settings; it changes nothing without asking.

## What's inside

- **Skills** — `project-plan`, `engineering`, `security`, `threat-model`,
  `quality-audit`, `setup`, and a design suite led by `design`.
- **Agents** — `researcher`, `reviewer`, `tester`, `implementer`.
- **Hooks** — session guidance that tells Claude when to use which skill, and a
  commit guard that blocks secrets and personal details.

## Evidence

In isolated evals against a no-plugin baseline, the right skill fired in
18 of 18 runs, and Launchpad raised scores where a capable model skips steps
on its own — regression tests, written plans, accessible UI. Full results and
caveats: [docs/evals/RESULTS.md](docs/evals/RESULTS.md).

## Development

```bash
uv sync
uv run ruff format --check scripts tests
uv run ruff check scripts tests
uv run pytest -q
uv run python scripts/check_plugin.py
claude plugin validate --strict .
```

## License

MIT. See [LICENSE](LICENSE).
