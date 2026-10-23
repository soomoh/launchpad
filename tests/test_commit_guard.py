"""Commit guard tests. Each builds a throwaway git repo in tmp_path with fabricated data.

Catastrophic failure modes pinned here:
- false allow: a staged secret or personal term reaches a commit
- secret echo: the block message repeats the secret into the transcript
- collateral block: an unrelated Bash command gets refused
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import commit_guard

FAKE_TOKEN = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"  # fabricated, right shape


@pytest.fixture(autouse=True)
def isolated_terms(monkeypatch, tmp_path):
    """Use only the project-level terms file, never the real ~/.claude one."""
    monkeypatch.setattr(commit_guard, "TERM_FILES", (Path(".privacy-terms"),))


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    run(root, "init", "-q")
    run(root, "config", "user.email", "test@example.invalid")
    run(root, "config", "user.name", "Test")
    write(root, "README.md", "hello\n")
    run(root, "add", "README.md")
    run(root, "commit", "-qm", "init")
    return root


def run(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def write(root: Path, name: str, text: str) -> None:
    (root / name).parent.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(text, encoding="utf-8")


def stage(root: Path, name: str, text: str) -> None:
    write(root, name, text)
    run(root, "add", name)


@pytest.mark.parametrize(
    "command",
    ["ls -la", "git status", "git log --oneline", "git commit-tree x", "npm test"],
)
def test_non_commit_commands_are_never_blocked(repo, command):
    stage(repo, "leak.py", f'token = "{FAKE_TOKEN}"\n')  # pragma: allowlist secret
    assert commit_guard.check_command(command, repo) is None


def test_quoted_mention_of_git_commit_is_treated_as_a_commit(repo):
    """Known, deliberate over-match: detection is textual, not a shell parse. It errs
    toward blocking, and only ever blocks when the staged content is unsafe anyway."""
    stage(repo, "app.py", "print('ok')\n")
    assert commit_guard.check_command("echo 'git commit later'", repo) is None
    stage(repo, "leak.py", f'token = "{FAKE_TOKEN}"\n')  # pragma: allowlist secret
    assert commit_guard.check_command("echo 'git commit later'", repo) is not None


def test_clean_commit_is_allowed(repo):
    stage(repo, "app.py", "print('ok')\n")
    assert commit_guard.check_command('git commit -m "add app"', repo) is None


@pytest.mark.parametrize(
    "line",
    [
        f'TOKEN = "{FAKE_TOKEN}"',  # pragma: allowlist secret
        'api_key = "abcd1234efgh5678"',  # pragma: allowlist secret
        "-----BEGIN OPENSSH PRIVATE KEY-----",  # pragma: allowlist secret
        "AWS_KEY=AKIAABCDEFGHIJKLMNOP",  # pragma: allowlist secret
        "key = sk-ant-api03-abcdefghijklmnopqrstuv",  # pragma: allowlist secret
    ],
)
def test_staged_secret_blocks_commit(repo, line):
    stage(repo, "config.py", line + "\n")
    reason = commit_guard.check_command("git commit -m x", repo)
    assert reason is not None and "secret" in reason


def test_block_message_never_echoes_the_secret(repo):
    stage(repo, "config.py", f'TOKEN = "{FAKE_TOKEN}"\n')  # pragma: allowlist secret
    reason = commit_guard.check_command("git commit -m x", repo)
    assert reason is not None
    assert FAKE_TOKEN not in reason


def test_allow_marker_exempts_a_reviewed_line(repo):
    stage(repo, "fixture.py", f'TOKEN = "{FAKE_TOKEN}"  # pragma: allowlist secret\n')
    assert commit_guard.check_command("git commit -m x", repo) is None


@pytest.mark.parametrize(
    ("name", "blocked"),
    [
        (".env", True),
        (".env.local", True),
        ("app/.env.production", True),
        (".env.example", False),
        (".env.local.example", False),  # real false positive (card-battler)
        ("config/.env.sample", False),
        ("deploy/server.pem", True),
        ("data/app.sqlite3", True),
        (".privacy-terms", True),
        ("src/environment.py", False),
    ],
)
def test_forbidden_files(repo, name, blocked):
    stage(repo, name, "x\n")
    reason = commit_guard.check_command("git commit -m x", repo)
    assert (reason is not None) == blocked


def test_home_directory_path_blocks_commit(repo):
    stage(repo, "notes.md", f"see {Path.home()}/projects/thing\n")
    reason = commit_guard.check_command("git commit -m x", repo)
    assert reason is not None and "personal term" in reason


def test_privacy_terms_file_entries_block_commit(repo):
    write(repo, ".privacy-terms", "# comment\nZanzibar Quill\nab\n")
    stage(repo, "about.md", "Written by zanzibar quill.\n")
    reason = commit_guard.check_command("git commit -m x", repo)
    assert reason is not None and "personal term" in reason


def test_short_terms_are_ignored(repo):
    write(repo, ".privacy-terms", "ab\n")
    stage(repo, "about.md", "ab ab ab\n")
    assert commit_guard.check_command("git commit -m x", repo) is None


def test_add_and_commit_in_one_command_is_refused(repo):
    # Written but not staged yet.
    write(repo, "config.py", f'TOKEN = "{FAKE_TOKEN}"\n')  # pragma: allowlist secret
    reason = commit_guard.check_command("git add . && git commit -m x", repo)
    assert reason is not None and "separate commands" in reason


def test_commit_all_scans_unstaged_tracked_changes(repo):
    # Tracked, modified, not staged.
    write(repo, "README.md", f'TOKEN = "{FAKE_TOKEN}"\n')  # pragma: allowlist secret
    assert commit_guard.check_command("git commit -m x", repo) is None
    assert commit_guard.check_command("git commit -am x", repo) is not None
    assert commit_guard.check_command("git commit --all -m x", repo) is not None


@pytest.mark.parametrize("form", ["git -C {d} commit -m x", "cd {d} && git commit -m x"])
def test_commit_in_another_directory_scans_that_repo(repo, tmp_path, form):
    stage(repo, "config.py", f'TOKEN = "{FAKE_TOKEN}"\n')  # pragma: allowlist secret
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    assert commit_guard.check_command(form.format(d=repo), elsewhere) is not None


def test_outside_a_repo_is_allowed(tmp_path):
    assert commit_guard.check_command("git commit -m x", tmp_path) is None


def test_history_scan_finds_a_secret_removed_later(repo):
    stage(repo, "config.py", f'TOKEN = "{FAKE_TOKEN}"\n')  # pragma: allowlist secret
    run(repo, "commit", "-qm", "oops")
    stage(repo, "config.py", "TOKEN = load()\n")
    run(repo, "commit", "-qm", "fix")
    problems = commit_guard.scan_history(repo)
    assert len(problems) == 1 and "secret" in problems[0]


@pytest.mark.parametrize("stdin", ["not json", "{}", '{"tool_input": {}}'])
def test_hook_ignores_unparseable_input(monkeypatch, stdin):
    monkeypatch.setattr(sys, "stdin", io.StringIO(stdin))
    assert commit_guard.hook_main() == 0


def test_hook_blocks_with_exit_2_and_reason_on_stderr(repo, monkeypatch, capsys):
    stage(repo, ".env", "X=1\n")
    payload = {"tool_input": {"command": "git commit -m x"}, "cwd": str(repo)}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    assert commit_guard.hook_main() == 2
    assert "forbidden file: .env" in capsys.readouterr().err


def test_history_with_non_utf8_bytes_is_scanned_not_crashed(repo):
    """Regression: a Latin-1 file in history crashed the scan (kardabra)."""
    (repo / "legacy.txt").write_bytes("caf\xe9 r\xe9sum\xe9\n".encode("latin-1"))
    run(repo, "add", "legacy.txt")
    run(repo, "commit", "-qm", "legacy")
    stage(repo, "config.py", f'TOKEN = "{FAKE_TOKEN}"\n')  # pragma: allowlist secret
    run(repo, "commit", "-qm", "oops")
    problems = commit_guard.scan_history(repo)
    assert len(problems) == 1 and "secret" in problems[0]
