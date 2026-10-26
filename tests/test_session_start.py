"""SessionStart hook tests. CLAUDE_CONFIG_DIR is pointed at tmp_path throughout; the real
~/.claude is never read.

Catastrophic failure modes pinned here:
- broken session: the hook exits non-zero or raises, which would disrupt every session
- ignored opt-out: guidance is still injected after the user switched it off
- silent drift: a changed or corrupt setup record produces no nudge
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import doctor
import session_start

ROOT = session_start.PLUGIN_ROOT

CORE_PHRASE = "Checkpoints — these always fire"


@pytest.fixture(autouse=True)
def cfg(monkeypatch, tmp_path) -> Path:
    path = tmp_path / "cfg"
    path.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(path))
    return path


@pytest.fixture
def data_dir(tmp_path) -> Path:
    return tmp_path / "data"


@pytest.mark.parametrize("option", ["false", "FALSE", "0", "no", "off", " Off "])
def test_off_values_inject_nothing(option, data_dir):
    assert session_start.build_context(option, data_dir) is None


@pytest.mark.parametrize("option", [None, "", "true"])
def test_on_values_inject_core_guidance(option):
    context = session_start.build_context(option, None)
    assert CORE_PHRASE in context


def test_no_data_dir_means_no_nudge():
    context = session_start.build_context(None, None)
    assert "## Setup" not in context
    assert session_start.FIRST_RUN not in context
    assert session_start.DRIFT not in context


def test_missing_record_nudges_first_run(data_dir):
    context = session_start.build_context(None, data_dir)
    assert session_start.FIRST_RUN in context
    assert CORE_PHRASE in context


def test_matching_fingerprint_has_no_nudge(data_dir):
    doctor.record(data_dir)
    context = session_start.build_context(None, data_dir)
    assert session_start.FIRST_RUN not in context
    assert session_start.DRIFT not in context
    assert "## Setup" not in context


def test_config_change_after_record_nudges_drift(cfg, data_dir):
    doctor.record(data_dir)
    (cfg / "CLAUDE.md").write_text("new rule\n", encoding="utf-8")
    context = session_start.build_context(None, data_dir)
    assert session_start.DRIFT in context
    assert session_start.FIRST_RUN not in context


# A record of the wrong JSON shape once made build_context raise, so the hook
# dropped all guidance instead of just nudging (regression).
@pytest.mark.parametrize(
    "content", ["not json", "", "[1]", '"text"'], ids=["text", "empty", "list", "string"]
)
def test_corrupt_record_is_first_run_not_a_crash(data_dir, content):
    data_dir.mkdir()
    (data_dir / doctor.SETUP_RECORD).write_text(content, encoding="utf-8")
    assert session_start.FIRST_RUN in session_start.build_context(None, data_dir)


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


def test_hook_absorbs_unexpected_record_shape(monkeypatch, tmp_path, capsys):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / doctor.SETUP_RECORD).write_text("[1]", encoding="utf-8")
    monkeypatch.setenv("CLAUDE_PLUGIN_DATA", str(data_dir))
    monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_INJECT_ROUTING", raising=False)
    assert session_start.main() == 0
    context = json.loads(capsys.readouterr().out)["hookSpecificOutput"]["additionalContext"]
    assert CORE_PHRASE in context  # guidance still delivered, not skipped


def test_hook_exits_cleanly_when_its_helper_module_is_broken(tmp_path):
    """A half-applied plugin update can leave doctor.py unimportable; the session
    must still start (exit 0), with the reason on stderr."""
    broken = tmp_path / "plugin" / "scripts"
    broken.mkdir(parents=True)
    (broken / "session_start.py").write_text(
        (ROOT / "scripts" / "session_start.py").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (broken / "doctor.py").write_text("this is not python(\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(broken / "session_start.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert result.stdout == ""
    assert "launchpad" in result.stderr
