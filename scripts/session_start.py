"""SessionStart hook: give Claude Launchpad's workflow guidance for this session.

Prints the hook JSON whose `additionalContext` Claude Code adds before the first
prompt: the core guidance (`guidance/core.md`). The `inject_routing` plugin option
turns it off.

A failure here must never break the user's session: any error is reported on stderr
and the hook still exits 0. Standard library only; runs on python3 3.10+.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
CORE = PLUGIN_ROOT / "guidance" / "core.md"
OFF_VALUES = {"false", "0", "no", "off"}


def build_context(option: str | None) -> str | None:
    """The text to inject, or None when the user switched the guidance off."""
    if (option or "").strip().lower() in OFF_VALUES:
        return None
    return CORE.read_text(encoding="utf-8").strip()


def main() -> int:
    try:
        context = build_context(os.environ.get("CLAUDE_PLUGIN_OPTION_INJECT_ROUTING"))
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
