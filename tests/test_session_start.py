"""SessionStart hook tests.

Catastrophic failure modes pinned here:
- broken session: the hook exits non-zero or raises, which would disrupt every session
- ignored opt-out: guidance is still injected after the user switched it off
- hidden nag: the hook injects anything beyond the core guidance
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import session_start

ROOT = session_start.PLUGIN_ROOT

CORE_PHRASE = "Checkpoints — these always fire"


@pytest.mark.parametrize("option", ["false", "FALSE", "0", "no", "off", " Off "])
def test_off_values_inject_nothing(option):
    assert session_start.build_context(option) is None


@pytest.mark.parametrize("option", [None, "", "true"])
def test_on_values_inject_core_guidance_only(option):
    context = session_start.build_context(option)
    assert context == session_start.CORE.read_text(encoding="utf-8").strip()
    assert CORE_PHRASE in context


def run_hook(tmp_path: Path, **extra: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("CLAUDE_")}
    env.update(
        CLAUDE_PLUGIN_DATA=str(tmp_path / "data"),
        CLAUDE_CONFIG_DIR=str(tmp_path / "cfg"),
        **extra,
    )
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "session_start.py")],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_hook_end_to_end_emits_session_start_json(tmp_path):
    result = run_hook(tmp_path)
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "SessionStart"
    assert CORE_PHRASE in output["additionalContext"]
    assert "/launchpad:setup" not in output["additionalContext"]
    assert not (tmp_path / "data").exists()  # the hook keeps no state


def test_hook_end_to_end_respects_opt_out(tmp_path):
    result = run_hook(tmp_path, CLAUDE_PLUGIN_OPTION_INJECT_ROUTING="false")
    assert result.returncode == 0
    assert result.stdout == ""


def test_hook_never_fails_the_session(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(session_start, "CORE", tmp_path / "missing.md")
    monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_INJECT_ROUTING", raising=False)
    assert session_start.main() == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "launchpad" in captured.err
