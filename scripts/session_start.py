"""SessionStart hook: give Claude Launchpad's workflow guidance for this session.

Prints the hook JSON whose `additionalContext` Claude Code adds before the first
prompt: the core guidance (`guidance/core.md`), plus a one-time-per-session nudge
when `/launchpad:setup` has never run or the user's configuration changed since it
last did. The `inject_routing` plugin option turns all of it off.

A failure here must never break the user's session: any error is reported on stderr
and the hook still exits 0. Standard library only; runs on python3 3.10+.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from doctor import PLUGIN_ROOT, SETUP_RECORD, fingerprint
except Exception as error:  # noqa: BLE001 - e.g. a half-applied plugin update
    print(f"launchpad: session guidance skipped ({error})", file=sys.stderr)
    sys.exit(0)  # never fail the user's session

CORE = PLUGIN_ROOT / "guidance" / "core.md"
OFF_VALUES = {"false", "0", "no", "off"}

FIRST_RUN = (
    "Launchpad's setup has not been run on this machine. Early in this session, at a "
    "natural pause, suggest once that the user run `/launchpad:setup`: it checks their "
    "existing Claude Code setup for conflicts with Launchpad and offers recommended "
    "safety settings. Don't repeat the suggestion if they decline."
)
DRIFT = (
    "The user's Claude Code configuration (global CLAUDE.md, settings, skills, or "
    "agents) changed since `/launchpad:setup` last checked it. Suggest once, at a "
    "natural pause, that they re-run it to catch new conflicts."
)


def setup_nudge(data_dir: Path | None, current: str) -> str | None:
    """The nudge to add, or None when setup's record matches the current config."""
    if data_dir is None:
        return None  # not running as an installed plugin; nowhere to keep a record
    try:
        recorded = json.loads((data_dir / SETUP_RECORD).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return FIRST_RUN
    except (OSError, ValueError):
        return FIRST_RUN  # an unreadable record is as good as none: re-run setup
    if not isinstance(recorded, dict):
        return FIRST_RUN  # wrong shape: treat like an unreadable record
    return None if recorded.get("fingerprint") == current else DRIFT


def build_context(option: str | None, data_dir: Path | None) -> str | None:
    """The text to inject, or None when the user switched the guidance off."""
    if (option or "").strip().lower() in OFF_VALUES:
        return None
    parts = [CORE.read_text(encoding="utf-8").strip()]
    nudge = setup_nudge(data_dir, fingerprint())
    if nudge:
        parts.append(f"## Setup\n\n{nudge}")
    return "\n\n".join(parts)


def main() -> int:
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    try:
        context = build_context(
            os.environ.get("CLAUDE_PLUGIN_OPTION_INJECT_ROUTING"),
            Path(data) if data else None,
        )
    except Exception as error:  # noqa: BLE001 - hook boundary: never break the session
        print(f"launchpad: session guidance skipped ({error})", file=sys.stderr)
        return 0
    if context:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        }
        print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
