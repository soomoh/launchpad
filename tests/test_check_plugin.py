"""Plugin consistency checker tests. Fake plugins are built in tmp_path.

Catastrophic failure modes pinned here:
- false pass: a broken reference, path, manifest, or hook script goes undetected, so a
  routing failure ships silently
- false alarm: a frontmatter `name:` or an allowed ~/.claude path fails the repo's own CI
- the real repo drifting out of consistency
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_plugin

ROOT = check_plugin.ROOT

SKILL = "---\nname: alpha\ndescription: does alpha things\n---\nUse launchpad:beta.\n"
AGENT = "---\nname: beta\ndescription: does beta things\nmodel: sonnet\n---\nBody.\n"


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def hooks_json(command: str = "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/x.py") -> str:
    hook = {"type": "command", "command": command}
    return json.dumps({"hooks": {"SessionStart": [{"hooks": [hook]}]}})


@pytest.fixture
def plugin(tmp_path) -> Path:
    root = tmp_path / "plugin"
    write(root, ".claude-plugin/plugin.json", json.dumps({"name": "launchpad"}))
    market = {"plugins": [{"name": "launchpad", "source": "./"}]}
    write(root, ".claude-plugin/marketplace.json", json.dumps(market))
    write(root, "hooks/hooks.json", hooks_json())
    write(root, "scripts/x.py", "")
    write(root, "guidance/core.md", "# Core\nShort.\n")
    write(root, "skills/alpha/SKILL.md", SKILL)
    write(root, "agents/beta.md", AGENT)
    return root


def test_real_repo_is_consistent():
    assert check_plugin.run_checks(ROOT) == []


def test_clean_fake_plugin_passes(plugin):
    assert check_plugin.run_checks(plugin) == []


def append(rel: str, text: str):
    def mutate(root: Path) -> None:
        path = root / rel
        path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")

    return mutate


def replace(rel: str, old: str, new: str):
    def mutate(root: Path) -> None:
        path = root / rel
        path.write_text(path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    return mutate


DEFECTS = [
    (
        "missing-ref",
        append("skills/alpha/SKILL.md", "See launchpad:missing.\n"),
        "launchpad:missing",
    ),
    (
        "bare-name",
        append("skills/alpha/SKILL.md", "Dispatch `beta` now.\n"),
        "without the `launchpad:`",
    ),
    ("bare-skill-name", append("agents/beta.md", "Run `/alpha`.\n"), "names `alpha`"),
    (
        "plugin-path",
        append("skills/alpha/SKILL.md", "Read ${CLAUDE_PLUGIN_ROOT}/nope.md\n"),
        "nope.md does not exist",
    ),
    (
        "personal-path",
        append("skills/alpha/SKILL.md", "Look in ~/.claude/skills/x\n"),
        "personal path",
    ),
    (
        "skill-name-mismatch",
        replace("skills/alpha/SKILL.md", "name: alpha", "name: gamma"),
        "frontmatter name is 'gamma'",
    ),
    (
        "skill-no-description",
        replace("skills/alpha/SKILL.md", "description: does alpha things\n", ""),
        "no description",
    ),
    ("agent-no-model", replace("agents/beta.md", "model: sonnet\n", ""), "missing model"),
    (
        "agent-name-mismatch",
        replace("agents/beta.md", "name: beta", "name: other"),
        "frontmatter name is 'other'",
    ),
    (
        "over-budget",
        append("guidance/core.md", "x" * check_plugin.GUIDANCE_BUDGET_CHARS),
        "budget is",
    ),
    (
        "hook-script-missing",
        lambda root: write(
            root, "hooks/hooks.json", hooks_json("${CLAUDE_PLUGIN_ROOT}/scripts/gone.py")
        ),
        "scripts/gone.py",
    ),
    (
        "marketplace-wrong-source",
        lambda root: write(
            root,
            ".claude-plugin/marketplace.json",
            json.dumps({"plugins": [{"name": "launchpad", "source": "./sub"}]}),
        ),
        "marketplace.json",
    ),
    (
        "plugin-wrong-name",
        lambda root: write(root, ".claude-plugin/plugin.json", json.dumps({"name": "other"})),
        "plugin.json name",
    ),
    # Review regressions: near-miss references that once slipped through.
    (
        "ref-uppercase",
        append("skills/alpha/SKILL.md", "\nUse `Launchpad:Beta`.\n"),
        "malformed reference",
    ),
    (
        "ref-space",
        append("skills/alpha/SKILL.md", "\nUse launchpad: beta.\n"),
        "malformed reference",
    ),
    (
        "ref-typo-suffix",
        append("skills/alpha/SKILL.md", "\nUse `launchpad:beta_x`.\n"),
        "not a skill or agent",
    ),
    (
        "ref-in-description",
        replace(
            "skills/alpha/SKILL.md", "description: ", "description: Pairs with launchpad:gamma. "
        ),
        "not a skill or agent",
    ),
    (
        "path-escapes-root",
        append("skills/alpha/SKILL.md", "\nRead ${CLAUDE_PLUGIN_ROOT}/../outside.md\n"),
        "leaves the plugin",
    ),
    (
        "manifest-unreadable",
        lambda root: write(root, "hooks/hooks.json", "{broken"),
        "manifest unreadable",
    ),
]


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [(m, e) for _, m, e in DEFECTS],
    ids=[name for name, _, _ in DEFECTS],
)
def test_each_defect_is_detected(plugin, mutate, expected):
    mutate(plugin)
    problems = check_plugin.run_checks(plugin)
    assert len(problems) == 1, problems
    assert expected in problems[0]


@pytest.mark.parametrize("path", ["~/.claude/privacy-terms.local", "~/.claude/.credentials.json"])
def test_documented_claude_paths_are_allowed(plugin, path):
    append("skills/alpha/SKILL.md", f"Reads {path}.\n")(plugin)
    assert check_plugin.run_checks(plugin) == []


def test_frontmatter_name_is_not_a_bare_reference(plugin):
    # The agent's own file says `name: beta`; only the body is scanned for references.
    assert "name: beta" in (plugin / "agents/beta.md").read_text(encoding="utf-8")
    assert check_plugin.check_references(plugin) == []


def test_skill_dir_without_skill_md_is_reported(plugin):
    (plugin / "skills" / "empty").mkdir()
    assert any("missing SKILL.md" in p for p in check_plugin.run_checks(plugin))
