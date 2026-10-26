"""Launchpad doctor: the deterministic half of `/launchpad:setup`.

Subcommands (each prints JSON on stdout):

- `check [--project DIR]` — what in the user's Claude Code setup could weaken or
  collide with Launchpad: hooks switched off, recommended permission rules missing,
  user skills or agents whose names overlap ours, and the instruction files the
  setup skill should read for conflicting rules. Reads only; changes nothing.
- `permissions [--apply]` — the recommended rules missing from the user's
  settings.json. With `--apply`, merges them in after writing a timestamped backup.
  Existing rules and every other setting are left as they were.
- `record --data-dir DIR` — stores a fingerprint of the user's configuration so the
  session-start hook can tell when it changes.

Everything stays on this machine; nothing here touches the network. Judging what the
findings mean (does a CLAUDE.md rule contradict ours?) is the setup skill's job.
Standard library only; runs on python3 3.10+.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import time
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent

# Claude's file tools can't read secrets in the usual places, and committing or pushing
# always asks first. Deny rules cover the Read tool only, not shell commands; the setup
# skill says so rather than overselling them.
RECOMMENDED = {
    "deny": [
        "Read(~/.ssh/**)",
        "Read(~/.aws/**)",
        "Read(~/.gnupg/**)",
        "Read(~/.claude/.credentials.json)",
        "Read(~/.claude/privacy-terms.local)",
        "Read(**/.privacy-terms)",
        "Read(**/.env)",
        "Read(**/.env.local)",
        "Read(**/.env.*.local)",
        "Read(**/.env.production)",
    ],
    "ask": [
        "Bash(git commit *)",
        "Bash(git push *)",
        "Bash(git push)",
    ],
}

SETUP_RECORD = "setup.json"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)
NAME_LINE = re.compile(r"^name:\s*(\S+)", re.MULTILINE)


def config_dir() -> Path:
    """The user's Claude Code config directory; CLAUDE_CONFIG_DIR relocates it."""
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def is_special(path: Path) -> bool:
    """True when `path` (followed through links) is a device, FIFO, or socket.

    Claude Code's sandbox mounts a /dev/null device at protected paths that don't
    exist yet, so a special file where settings belong means "no file". Stat
    errors return False so the caller's own read reports them (e.g. a link loop).
    """
    try:
        mode = path.stat().st_mode
    except OSError:
        return False
    return not (stat.S_ISREG(mode) or stat.S_ISDIR(mode))


def read_json(path: Path) -> tuple[dict | None, str | None]:
    """(parsed object, None), (None, error) when unusable, or (None, None) when absent.

    Absent includes a special file (see is_special); a directory is an error.
    """
    try:
        # Checked before opening: a placeholder device fails with EACCES, a FIFO hangs.
        if is_special(path):
            return None, None
        # utf-8-sig: editors on Windows often save settings with a byte-order mark.
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, None
    except OSError as error:
        return None, f"{path} could not be read ({error}); check it exists and is readable."
    except (ValueError, RecursionError) as error:
        return (
            None,
            f"{path} isn't valid JSON ({error}). Comments and trailing commas aren't "
            "allowed; fix or move the file, then run setup again.",
        )
    if not isinstance(data, dict):
        return None, f"{path} should hold a JSON object; fix or move it first."
    return data, None


def agent_name(path: Path) -> str:
    """An agent's name from its frontmatter, falling back to the file stem."""
    try:
        block = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        block = None
    match = NAME_LINE.search(block.group(1)) if block else None
    return match.group(1) if match else path.stem


def our_names() -> dict[str, set[str]]:
    return {
        "skill": {p.parent.name for p in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")},
        "agent": {agent_name(p) for p in (PLUGIN_ROOT / "agents").glob("*.md")},
    }


def stays_inside(path: Path, root: Path) -> bool:
    """False when `path` (a symlink, typically) resolves outside `root`.

    A cloned repo is untrusted: its CLAUDE.md or .claude/agents/x.md could be a link
    to a secret elsewhere on disk, which setup would then read into the conversation.
    The user's own config dir is trusted, so links there (dotfile repos) are fine.
    """
    try:
        return path.resolve().is_relative_to(root.resolve())
    except OSError:
        return False


def user_definitions(root: Path, trusted: bool) -> list[tuple[str, str, Path]]:
    """(kind, name, path) for every skill and agent defined under `root`.

    An untrusted root (a project's .claude/) skips links that lead outside it.
    """

    def keep(path: Path) -> bool:
        return path.is_file() and (trusted or stays_inside(path, root))

    skills = [p for p in root.glob("skills/*/SKILL.md") if keep(p)]
    agents = [p for p in root.glob("agents/*.md") if keep(p)]
    return [("skill", p.parent.name, p) for p in skills] + [
        ("agent", agent_name(p), p) for p in agents
    ]


def check(project: Path) -> dict:
    """Findings for the setup skill to explain. Reads only."""
    home = config_dir()
    project_config = project / ".claude"
    settings_files = [
        home / "settings.json",
        project_config / "settings.json",
        project_config / "settings.local.json",
    ]
    errors, hooks_disabled = [], []
    for path in settings_files:
        data, error = read_json(path)
        if error:
            errors.append(error)
        elif data and data.get("disableAllHooks") is True:
            hooks_disabled.append(str(path))

    ours = our_names()
    overlaps = [
        {"kind": kind, "name": name, "path": str(path)}
        for kind, name, path in sorted(
            user_definitions(home, trusted=True) + user_definitions(project_config, trusted=False)
        )
        if name in ours[kind]
    ]
    project_files = [project / n for n in ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md")]
    instruction_files = [str(home / "CLAUDE.md")] if (home / "CLAUDE.md").is_file() else []
    instruction_files += [str(p) for p in project_files if p.is_file() and stays_inside(p, project)]
    missing, permission_error = missing_permissions()
    if permission_error:
        errors.append(permission_error)
    return {
        "python": sys.version.split()[0],
        "config_dir": str(home),
        "errors": sorted(set(errors)),
        "hooks_disabled_in": hooks_disabled,
        "missing_permissions": missing,
        "name_overlaps": overlaps,
        "instruction_files": instruction_files,
    }


def missing_permissions() -> tuple[dict[str, list[str]], str | None]:
    """Recommended rules not yet in the user's settings.json, or an error to report."""
    path = config_dir() / "settings.json"
    settings, error = read_json(path)
    if error:
        return {}, error
    return missing_from(settings, path)


def missing_from(settings: dict | None, path: Path) -> tuple[dict[str, list[str]], str | None]:
    """Recommended rules absent from already-parsed settings, or a shape error."""
    # Only an absent key means "no rules yet". A present but falsy value ([] or "")
    # is a malformed shape and must reach the check below, not become {}.
    permissions = (settings or {}).get("permissions", {})
    if not isinstance(permissions, dict) or any(
        not isinstance(permissions.get(kind, []), list) for kind in RECOMMENDED
    ):
        return {}, (
            f"{path}: `permissions` should be an object whose `deny` and `ask` are "
            "lists; fix it by hand, then run setup again."
        )
    missing = {
        kind: [rule for rule in rules if rule not in (permissions.get(kind) or [])]
        for kind, rules in RECOMMENDED.items()
    }
    return {kind: rules for kind, rules in missing.items() if rules}, None


def backup_copy(target: Path) -> Path:
    """Copy `target` to a new, never-overwritten backup beside it, keeping its mode."""
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for attempt in range(100):
        suffix = f"-{attempt}" if attempt else ""
        backup = target.with_name(f"{target.name}.launchpad-backup-{stamp}{suffix}")
        try:
            # "x" fails if the name exists, so two runs in one second can't collide.
            with backup.open("xb") as out, target.open("rb") as src:
                shutil.copyfileobj(src, out)
        except FileExistsError:
            continue
        shutil.copymode(target, backup)  # settings can hold tokens; keep them private
        return backup
    raise RuntimeError(f"could not find a free backup name beside {target}")


def write_atomically(target: Path, text: str) -> None:
    """Replace `target` so a crash leaves either the old file or the new one, never half.

    Writes a temp file in the same directory (same filesystem, so the rename is
    atomic), copies the original's mode, syncs it to disk, then renames over.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", delete=False
    )
    try:
        with tmp:
            tmp.write(text)
            tmp.flush()
            os.fsync(tmp.fileno())
        if target.exists():
            shutil.copymode(target, tmp.name)
        os.replace(tmp.name, target)
    except BaseException:
        Path(tmp.name).unlink(missing_ok=True)
        raise


def apply_permissions() -> dict:
    """Merge the missing rules into settings.json after backing it up."""
    # Write through a symlinked settings.json (dotfile repos) to its real file, so
    # the link survives the atomic rename.
    path = (config_dir() / "settings.json").resolve()
    if is_special(path):
        # read_json calls this absent, but backing up or replacing it would be wrong:
        # it's a sandbox placeholder, or a link to a device such as /dev/null.
        return {
            "applied": False,
            "error": f"{path} isn't a regular file (Claude Code's sandbox puts a "
            "placeholder device at protected paths); it was left unchanged. Run setup "
            "outside the sandbox, or replace it with a real settings.json.",
        }
    settings, error = read_json(path)  # read once: what we check is what we write
    if not error:
        missing, error = missing_from(settings, path)
    if error:
        return {"applied": False, "error": error}
    if not missing:
        return {"applied": False, "added": {}, "note": "All recommended rules present."}
    settings = settings or {}
    permissions = settings.setdefault("permissions", {})
    for kind, rules in missing.items():
        permissions.setdefault(kind, [])
        permissions[kind] += rules
    try:
        backup = backup_copy(path) if path.exists() else None
        write_atomically(path, json.dumps(settings, indent=2, ensure_ascii=False) + "\n")
    except OSError as error:
        return {
            "applied": False,
            "error": f"couldn't update {path} ({error}); it was left unchanged. "
            "Check that the folder is writable, then run setup again.",
        }
    return {
        "applied": True,
        "added": missing,
        "backup": str(backup) if backup else None,
    }


def fingerprint() -> str:
    """Hash of the user-level configuration that can change how Launchpad behaves.

    Only the parts setup actually judges: the global CLAUDE.md, whether hooks are
    off, which recommended rules are present, and skill/agent names. Hashing all of
    settings.json would nudge after every unrelated change Claude Code writes there.
    """
    home = config_dir()
    digest = hashlib.sha256()
    try:
        digest.update((home / "CLAUDE.md").read_bytes())
    except OSError:
        digest.update(b"<absent>")
    settings, _ = read_json(home / "settings.json")
    settings = settings or {}
    permissions = settings.get("permissions")
    permissions = permissions if isinstance(permissions, dict) else {}
    present = sorted(
        f"{kind}:{rule}"
        for kind, rules in RECOMMENDED.items()
        for rule in rules
        if isinstance(permissions.get(kind), list) and rule in permissions[kind]
    )
    relevant = {"disableAllHooks": settings.get("disableAllHooks"), "rules": present}
    digest.update(b"\0" + json.dumps(relevant, sort_keys=True).encode())
    for kind, name, _ in sorted(user_definitions(home, trusted=True)):
        digest.update(f"\0{kind}:{name}".encode())
    return digest.hexdigest()


def record(data_dir: Path) -> dict:
    # An unsubstituted ${CLAUDE_PLUGIN_DATA} arrives as "" (= the current directory):
    # refuse rather than drop setup.json into the user's project.
    if not data_dir.is_absolute():
        return {
            "recorded": False,
            "error": f"--data-dir must be an absolute path, got {str(data_dir)!r}. "
            "Launchpad's data directory wasn't provided; nothing was recorded.",
        }
    entry = {"fingerprint": fingerprint(), "recorded_at": int(time.time())}
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / SETUP_RECORD).write_text(json.dumps(entry) + "\n", encoding="utf-8")
    except OSError as error:
        return {"recorded": False, "error": f"couldn't write to {data_dir} ({error})."}
    return {"recorded": True, "path": str(data_dir / SETUP_RECORD)}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    check_cmd = commands.add_parser("check")
    check_cmd.add_argument("--project", type=Path, default=Path.cwd())
    perm_cmd = commands.add_parser("permissions")
    perm_cmd.add_argument("--apply", action="store_true")
    record_cmd = commands.add_parser("record")
    record_cmd.add_argument("--data-dir", required=True)
    args = parser.parse_args(argv)

    if args.command == "check":
        result = check(args.project.resolve())
    elif args.command == "permissions" and args.apply:
        result = apply_permissions()
    elif args.command == "permissions":
        missing, error = missing_permissions()
        result = {"missing": missing, "error": error}
    else:
        result = record(Path(args.data_dir))
    print(json.dumps(result, indent=2))
    return 1 if result.get("error") else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
