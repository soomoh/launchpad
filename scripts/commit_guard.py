"""Commit guard: secrets and personal details never reach a commit Claude makes.

Two entry points, one scanner:

- Hook mode (no arguments): Claude Code's PreToolUse hook pipes the Bash call as JSON on
  stdin. Non-commit commands exit 0 immediately. For a `git commit`, the staged changes
  are scanned; any finding exits 2, which blocks the command and shows Claude the reason.
- Audit mode (`--staged`, `--history`): prints findings for a repo, exit 1 if any. The
  quality-audit skill uses `--history` to check every commit ever made, since a secret
  deleted in a later commit is still published by the first push.

Personal terms come from files outside any repo (see TERM_FILES), so this script never
contains them. Standard library only; must run on the system python3 (3.10).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

# Files that must never be committed, matched against the path. Templates are allowed:
# TEMPLATE_PATH is checked first, so `.env.example` and `.env.local.example` pass.
TEMPLATE_PATH = re.compile(r"\.(example|sample|template)$", re.IGNORECASE)
FORBIDDEN_PATH = re.compile(
    r"(^|/)\.env(\..+)?$"
    r"|(^|/)\.privacy-terms$"
    r"|(^|/)id_(rsa|dsa|ecdsa|ed25519)$"
    r"|\.(pem|key|p12|pfx|keystore|jks)$"
    r"|\.(db|db-journal|sqlite3?)$"
    r"|(^|/)credentials\.json$",
    re.IGNORECASE,
)

# Known token shapes first (precise), then the generic `name = "value"` assignment.
SECRET = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|\bAKIA[0-9A-Z]{16}\b"
    r"|\bgh[pousr]_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b"
    r"|\bsk-ant-[A-Za-z0-9_-]{20,}"
    r"|\bsk-(proj-)?[A-Za-z0-9]{32,}\b"
    r"|\bxox[abposr]-[A-Za-z0-9-]{10,}"
    r"|\bAIza[0-9A-Za-z_-]{35}\b"
    r"""|(api[_-]?key|secret|passw(or)?d|token)\s*[:=]\s*["'][^"'\s]{8,}["']""",
    re.IGNORECASE,
)
# detect-secrets' convention: a reviewed false positive is marked on its own line.
ALLOW_MARKER = "pragma: allowlist secret"

# One private term per line. Neither file is ever committed: the global one lives in
# ~/.claude (excluded by its allowlist .gitignore); the project one must be gitignored,
# and FORBIDDEN_PATH blocks it if staged anyway.
TERM_FILES = (Path.home() / ".claude" / "privacy-terms.local", Path(".privacy-terms"))
# Shorter terms would match ordinary words.
MIN_TERM_CHARS = 4

# The subcommand must end at whitespace or a shell separator, so `git commit-tree` and
# `git add-on` style names don't count.
GIT_COMMIT = re.compile(r"\bgit\b(?:\s+-[cC]\s+\S+)*\s+commit(?=$|[\s;&|)])")
GIT_ADD = re.compile(r"\bgit\b(?:\s+-[cC]\s+\S+)*\s+add(?=$|[\s;&|)])")
GIT_DIR_FLAG = re.compile(r"\bgit\s+-C\s+(\"[^\"]+\"|'[^']+'|\S+)")
LEADING_CD = re.compile(r"^\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)\s*(&&|;)")
COMMIT_ALL_FLAG = re.compile(r"\s(-a\b|-[a-zA-Z]*a[a-zA-Z]*\b|--all\b)")


class Line(NamedTuple):
    path: str
    text: str  # an added line, without its leading "+"


def personal_terms(root: Path) -> set[str]:
    """Lowercased private terms: the home directory path plus the TERM_FILES entries."""
    terms = {str(Path.home())}
    for term_file in TERM_FILES:
        path = term_file if term_file.is_absolute() else root / term_file
        try:
            terms.update(path.read_text(encoding="utf-8").splitlines())
        except OSError:
            continue  # an absent terms file is normal, not an error
    cleaned = (t.strip().lower() for t in terms)
    return {t for t in cleaned if len(t) >= MIN_TERM_CHARS and not t.startswith("#")}


def find_problems(paths: list[str], added: list[Line], terms: set[str]) -> list[str]:
    """Reasons to block, one line each; empty means safe. Never echoes the secret itself."""
    problems = [
        f"forbidden file: {p}"
        for p in paths
        if FORBIDDEN_PATH.search(p) and not TEMPLATE_PATH.search(p)
    ]
    term_patterns = [re.compile(rf"(?<!\w){re.escape(t)}(?!\w)", re.IGNORECASE) for t in terms]
    for line in added:
        if ALLOW_MARKER in line.text:
            continue
        if SECRET.search(line.text):
            problems.append(f"{line.path}: adds what looks like a secret")
        if any(p.search(line.text) for p in term_patterns):
            problems.append(f"{line.path}: adds a personal term (home path or privacy-terms entry)")
    return sorted(set(problems))


def parse_diff(diff: str) -> tuple[list[str], list[Line]]:
    """(paths touched, added lines) from `git diff`/`git log -p` output with -U0."""
    paths: list[str] = []
    added: list[Line] = []
    current = ""
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            current = raw[6:] if raw.startswith("+++ b/") else raw[4:]
            if current != "/dev/null":
                paths.append(current)
        elif raw.startswith("+") and not raw.startswith("+++"):
            added.append(Line(current, raw[1:]))
    return paths, added


def git(root: Path, *args: str) -> str:
    # History and diffs can hold non-UTF-8 bytes (old encodings, binary-ish text).
    # Replacing them keeps the scan going; the ASCII patterns it looks for survive.
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    ).stdout


def scan_staged(root: Path, include_unstaged_tracked: bool = False) -> list[str]:
    """Findings for what the next commit would contain."""
    diff = git(root, "diff", "--cached", "-U0", "--no-color")
    if include_unstaged_tracked:  # `git commit -a` also takes tracked, unstaged edits
        diff += "\n" + git(root, "diff", "-U0", "--no-color")
    paths, added = parse_diff(diff)
    return find_problems(paths, added, personal_terms(root))


def scan_history(root: Path) -> list[str]:
    """Findings across every commit on every branch, prefixed with the commit."""
    problems: list[str] = []
    terms = personal_terms(root)
    log = git(root, "log", "--all", "-p", "-U0", "--no-color", "--format=@@commit %h")
    for chunk in log.split("@@commit ")[1:]:
        sha, _, diff = chunk.partition("\n")
        paths, added = parse_diff(diff)
        problems += [f"{sha}: {p}" for p in find_problems(paths, added, terms)]
    return problems


def repo_root_for(command: str, cwd: Path) -> Path:
    """Where the commit in `command` runs: honours `git -C dir` and a leading `cd dir &&`."""
    for pattern in (GIT_DIR_FLAG, LEADING_CD):
        match = pattern.search(command)
        if match:
            return (cwd / Path(match.group(1).strip("\"'")).expanduser()).resolve()
    return cwd


def check_command(command: str, cwd: Path) -> str | None:
    """Hook decision for one Bash command: None to allow, or the reason to block."""
    commit = GIT_COMMIT.search(command)
    if commit is None:
        return None
    # The hook runs before the whole command, so files added in the same command are not
    # staged yet and the scan would miss them.
    if GIT_ADD.search(command[: commit.start()]):
        return (
            "commit guard: run `git add` and `git commit` as separate commands, "
            "so the guard can scan what is actually staged."
        )
    try:
        root = Path(git(repo_root_for(command, cwd), "rev-parse", "--show-toplevel").strip())
    except (subprocess.CalledProcessError, OSError):
        return None  # not a repo: git commit will fail on its own
    commit_all = bool(COMMIT_ALL_FLAG.search(command[commit.end() :]))
    problems = scan_staged(root, include_unstaged_tracked=commit_all)
    if not problems:
        return None
    lines = "\n".join(f"  - {p}" for p in problems)
    return (
        "commit guard: blocked. Unstage or fix these, then commit again. A reviewed false "
        f"positive can be marked with `{ALLOW_MARKER}` on that line.\n{lines}"
    )


def hook_main() -> int:
    try:
        payload = json.load(sys.stdin)
        command = payload["tool_input"]["command"]
        cwd = Path(payload.get("cwd") or Path.cwd())
    except (json.JSONDecodeError, KeyError, TypeError):
        return 0  # not a Bash call we understand; never block unrelated tools
    try:
        reason = check_command(command, cwd)
    except Exception as error:  # noqa: BLE001 - hook boundary: fail closed on commits
        reason = f"commit guard: could not scan the commit ({error}); refusing to allow it."
    if reason is None:
        return 0
    print(reason, file=sys.stderr)
    return 2  # PreToolUse exit 2: block the tool call, stderr goes to Claude


def audit_main(mode: str, target: str) -> int:
    root = Path(git(Path(target).resolve(), "rev-parse", "--show-toplevel").strip())
    problems = scan_history(root) if mode == "--history" else scan_staged(root)
    for problem in problems:
        print(problem)
    print(f"{len(problems)} finding(s) in {root} ({mode.lstrip('-')})")
    return 1 if problems else 0


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] in ("--staged", "--history"):
        sys.exit(audit_main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "."))
    sys.exit(hook_main())
