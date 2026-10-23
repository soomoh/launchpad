# Contributing

Thanks for helping. Launchpad is a Claude Code plugin made of Markdown skills
and agents plus a few small Python scripts (standard library only, Python
3.10+).

## Layout

| Path | What it is |
|---|---|
| `skills/<name>/SKILL.md` | One skill each. The `description` decides when it fires |
| `agents/*.md` | The four subagents |
| `guidance/core.md` | Guidance added to every session: priorities and when to use which skill |
| `hooks/hooks.json` | Runs `scripts/session_start.py` at session start and `scripts/commit_guard.py` before shell commands |
| `scripts/doctor.py` | The checks and settings merge behind `/launchpad:setup` |
| `scripts/check_plugin.py` | Consistency checks for the whole plugin |
| `evals/` | Behaviour tests run with `claude plugin eval` |
| `tests/` | pytest tests for the scripts |

## Checks

Run these before opening a pull request; CI runs the same ones.

```bash
uv sync
uv run ruff format --check scripts tests
uv run ruff check scripts tests
uv run pytest -q
uv run python scripts/check_plugin.py
claude plugin validate --strict .
```

To try your changes in a real session without installing:

```bash
claude --plugin-dir /path/to/launchpad
```

## Rules that keep it working

- Refer to skills and agents by their full name, `launchpad:<name>`. A bare
  name doesn't resolve once the plugin is installed; the checker catches it.
- In skills, point at plugin files with `${CLAUDE_PLUGIN_ROOT}/...`.
- Scripts never use the network, never crash a session, and change a user's
  settings only after they agree.
- The design skills' concrete rules (numbers, CSS names) are pinned by
  `tests/test_design_rules.py`. If you change one on purpose, regenerate the
  snapshot with `uv run python tests/test_design_rules.py --write` and include
  the diff.

## Behaviour evals

`evals/` holds cases that compare Claude with and without the plugin. They
use your own Claude usage, so run them when you change a skill's wording or
the guidance:

```bash
claude plugin eval . --runs 3 --model sonnet --allow-tools Write --no-publish
```

Keep `--no-publish`: reports contain full transcripts. Results are written to
`evals/results/`, which is gitignored. See
[docs/evals/RESULTS.md](docs/evals/RESULTS.md) for the latest summary.
