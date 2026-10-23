"""Check that the plugin hangs together. Run after changing any skill, agent, hook,
or the guidance; CI runs it too:

    python3 scripts/check_plugin.py

Checks: skill and agent frontmatter; every `launchpad:<name>` reference resolves to
a skill or agent we ship; no skill or agent of ours is named without the prefix (a
bare name doesn't resolve once installed, so routing would fail silently); every
`${CLAUDE_PLUGIN_ROOT}/…` path exists; no personal `~/.claude/` paths beyond the
documented ones; the manifests agree; hook scripts exist; and the injected guidance
stays within its size budget. Prints one line per problem; exit 1 if any.
Standard library only; runs on python3 3.10+.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIX = "launchpad"

# Injected into every session, so it is paid for every session. Claude Code's own
# hard cap is 10,000 characters; past that it truncates to a preview.
GUIDANCE_BUDGET_CHARS = 6000

# `~/.claude/` paths that are deliberate: the optional private-terms file and the
# credentials file the recommended deny rules protect.
ALLOWED_CLAUDE_PATHS = {"~/.claude/privacy-terms.local", "~/.claude/.credentials.json"}

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# Deliberately loose (any case, optional space, underscores) so near-misses such as
# `Launchpad:Reviewer` or `launchpad:reviewer_x` are caught and reported, not skipped.
NAMESPACED_REF = re.compile(rf"\b{PREFIX}:\s?([A-Za-z0-9_-]+)", re.IGNORECASE)
BACKTICKED = re.compile(r"`/?([a-z][a-z0-9-]*)`")
PLUGIN_PATH = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]*[A-Za-z0-9_])")
CLAUDE_PATH = re.compile(r"~/\.claude/[A-Za-z0-9_./*-]*[A-Za-z0-9_]")


def frontmatter(path: Path) -> dict[str, str]:
    """Top-level `key: value` pairs from a file's YAML frontmatter; {} if absent."""
    match = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if match is None:
        return {}
    pairs = (line.split(":", 1) for line in match.group(1).splitlines() if ":" in line)
    return {key.strip(): value.strip() for key, value in pairs}


def body(path: Path) -> str:
    """File text with any frontmatter removed (its `name:` is not a reference)."""
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    return text[match.end() :] if match else text


def skill_names(root: Path) -> set[str]:
    return {p.parent.name for p in (root / "skills").glob("*/SKILL.md")}


def agent_names(root: Path) -> set[str]:
    return {p.stem for p in (root / "agents").glob("*.md")}


def documents(root: Path) -> list[Path]:
    """Every instruction file whose references must resolve."""
    docs = sorted((root / "skills").rglob("*.md")) + sorted((root / "agents").glob("*.md"))
    return docs + sorted((root / "guidance").glob("*.md"))


def check_definitions(root: Path) -> list[str]:
    problems = []
    for skill_dir in sorted(p for p in (root / "skills").iterdir() if p.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            problems.append(f"skills/{skill_dir.name}: missing SKILL.md")
            continue
        meta = frontmatter(skill_file)
        if meta.get("name") != skill_dir.name:
            problems.append(f"skills/{skill_dir.name}: frontmatter name is {meta.get('name')!r}")
        if not meta.get("description"):
            problems.append(f"skills/{skill_dir.name}: no description, so it can never trigger")
    for agent in sorted((root / "agents").glob("*.md")):
        meta = frontmatter(agent)
        if meta.get("name") != agent.stem:
            problems.append(f"agents/{agent.name}: frontmatter name is {meta.get('name')!r}")
        for key in ("description", "model"):
            if not meta.get(key):
                problems.append(f"agents/{agent.name}: missing {key}")
    return problems


def check_references(root: Path) -> list[str]:
    ours = skill_names(root) | agent_names(root)
    problems = []
    for doc in documents(root):
        full = doc.read_text(encoding="utf-8")  # includes frontmatter descriptions
        text = body(doc)
        where = doc.relative_to(root)
        for match in sorted({m.group(0) for m in NAMESPACED_REF.finditer(full)}):
            name = NAMESPACED_REF.match(match).group(1)
            if match != f"{PREFIX}:{name}":
                problems.append(f"{where}: malformed reference `{match}`")
            elif name not in ours:
                problems.append(f"{where}: `{match}` is not a skill or agent we ship")
        for name in sorted(set(BACKTICKED.findall(text)) & ours):
            problems.append(f"{where}: names `{name}` without the `{PREFIX}:` prefix")
        for rel in sorted(set(PLUGIN_PATH.findall(text))):
            if ".." in Path(rel).parts:
                problems.append(f"{where}: path ${{CLAUDE_PLUGIN_ROOT}}/{rel} leaves the plugin")
            elif not (root / rel).exists():
                problems.append(f"{where}: path ${{CLAUDE_PLUGIN_ROOT}}/{rel} does not exist")
        for raw in sorted(set(CLAUDE_PATH.findall(text)) - ALLOWED_CLAUDE_PATHS):
            problems.append(f"{where}: personal path {raw}; use ${{CLAUDE_PLUGIN_ROOT}}")
    return problems


def check_manifests(root: Path) -> list[str]:
    try:
        plugin = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        market = json.loads(
            (root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")
        )
        hooks = json.loads((root / "hooks" / "hooks.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return [f"manifest unreadable: {error}"]
    problems = []
    if plugin.get("name") != PREFIX:
        problems.append(f"plugin.json name is {plugin.get('name')!r}, expected {PREFIX!r}")
    entries = [p for p in market.get("plugins", []) if p.get("name") == PREFIX]
    if len(entries) != 1 or entries[0].get("source") != "./":
        problems.append("marketplace.json needs one `launchpad` entry with source `./`")
    commands = [
        hook["command"]
        for groups in hooks.get("hooks", {}).values()
        for group in groups
        for hook in group.get("hooks", [])
        if hook.get("type") == "command"
    ]
    for command in commands:
        for rel in PLUGIN_PATH.findall(command):
            if not (root / rel).is_file():
                problems.append(f"hooks.json runs {rel}, which does not exist")
    return problems


def check_budget(root: Path) -> list[str]:
    size = len((root / "guidance" / "core.md").read_text(encoding="utf-8"))
    if size > GUIDANCE_BUDGET_CHARS:
        return [f"guidance/core.md is {size} chars; budget is {GUIDANCE_BUDGET_CHARS}"]
    return []


def run_checks(root: Path) -> list[str]:
    return (
        check_definitions(root)
        + check_references(root)
        + check_manifests(root)
        + check_budget(root)
    )


def main() -> int:
    problems = run_checks(ROOT)
    for problem in problems:
        print(problem)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
