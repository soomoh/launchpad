"""Doctor tests. Every test points CLAUDE_CONFIG_DIR at tmp_path; the real ~/.claude is
never read or written.

Catastrophic failure modes pinned here:
- settings loss: apply_permissions drops, rewrites, or duplicates the user's settings
- clobbering malformed config: apply overwrites a settings.json it could not understand
- silent weakening: disabled hooks or a broken settings file go unreported
- false overlap: a `name:` in an agent's body (not frontmatter) is taken as its name
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import doctor


@pytest.fixture(autouse=True)
def cfg(monkeypatch, tmp_path) -> Path:
    path = tmp_path / "cfg"
    path.mkdir()
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(path))
    return path


@pytest.fixture
def project(tmp_path) -> Path:
    path = tmp_path / "proj"
    path.mkdir()
    return path


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def all_recommended() -> list[str]:
    return [rule for rules in doctor.RECOMMENDED.values() for rule in rules]


def test_empty_config_has_no_findings_and_all_rules_missing(project):
    result = doctor.check(project)
    assert result["errors"] == []
    assert result["name_overlaps"] == []
    assert result["hooks_disabled_in"] == []
    assert result["instruction_files"] == []
    assert result["missing_permissions"] == doctor.RECOMMENDED


@pytest.mark.parametrize("where", ["user", "project-local"])
def test_disable_all_hooks_is_reported(cfg, project, where):
    target = (
        cfg / "settings.json" if where == "user" else project / ".claude" / "settings.local.json"
    )
    write(target, json.dumps({"disableAllHooks": True}))
    assert doctor.check(project)["hooks_disabled_in"] == [str(target)]


def test_hooks_not_disabled_when_false(cfg, project):
    write(cfg / "settings.json", json.dumps({"disableAllHooks": False}))
    assert doctor.check(project)["hooks_disabled_in"] == []


@pytest.mark.parametrize("content", ["{not json", "[1, 2]"], ids=["invalid", "list"])
def test_malformed_settings_reported_not_raised(cfg, project, content):
    write(cfg / "settings.json", content)
    result = doctor.check(project)
    assert any(str(cfg / "settings.json") in e for e in result["errors"])


def test_agent_overlap_uses_frontmatter_name_not_filename(cfg, project):
    write(cfg / "agents" / "my-rev.md", "---\nname: reviewer\n---\nbody\n")
    overlaps = doctor.check(project)["name_overlaps"]
    assert [(o["kind"], o["name"]) for o in overlaps] == [("agent", "reviewer")]


def test_skill_overlap_detected(cfg, project):
    write(cfg / "skills" / "security" / "SKILL.md", "---\nname: security\n---\n")
    overlaps = doctor.check(project)["name_overlaps"]
    assert [(o["kind"], o["name"]) for o in overlaps] == [("skill", "security")]


def test_project_level_overlap_detected(project):
    write(project / ".claude" / "skills" / "design" / "SKILL.md", "x")
    overlaps = doctor.check(project)["name_overlaps"]
    assert [(o["kind"], o["name"]) for o in overlaps] == [("skill", "design")]


def test_non_overlapping_names_not_reported(cfg, project):
    write(cfg / "agents" / "mine.md", "---\nname: totally-custom\n---\n")
    write(cfg / "skills" / "custom-thing" / "SKILL.md", "x")
    assert doctor.check(project)["name_overlaps"] == []


def test_name_line_in_body_is_not_the_name(cfg):
    path = write(
        cfg / "agents" / "mine.md",
        "---\ndescription: d\n---\nname: reviewer\n",
    )
    assert doctor.agent_name(path) == "mine"  # falls back to stem


def test_agent_without_frontmatter_falls_back_to_stem(cfg):
    path = write(cfg / "agents" / "plain.md", "name: reviewer\n")
    assert doctor.agent_name(path) == "plain"


def test_instruction_files_lists_existing_only(cfg, project):
    user = write(cfg / "CLAUDE.md", "x")
    proj = write(project / "CLAUDE.md", "x")
    local = write(project / "CLAUDE.local.md", "x")
    assert doctor.check(project)["instruction_files"] == [str(user), str(proj), str(local)]


# --- apply_permissions: CATASTROPHIC -------------------------------------------------


def test_apply_never_loses_user_settings(cfg):
    existing_deny = doctor.RECOMMENDED["deny"][0]
    original = {
        "model": "opus",
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": []}]},
        "permissions": {
            "deny": [existing_deny],
            "ask": ["Bash(rm *)"],
            "allow": ["Bash(ls)"],
        },
    }
    path = write(cfg / "settings.json", json.dumps(original))
    original_bytes = path.read_bytes()

    result = doctor.apply_permissions()
    assert result["applied"] is True

    after = json.loads(path.read_text(encoding="utf-8"))
    assert after["model"] == original["model"]
    assert after["hooks"] == original["hooks"]
    assert after["permissions"]["allow"] == ["Bash(ls)"]
    assert "Bash(rm *)" in after["permissions"]["ask"]
    for kind in ("deny", "ask"):
        rules = after["permissions"][kind]
        assert len(rules) == len(set(rules)), f"duplicate in {kind}"
        for rule in doctor.RECOMMENDED[kind]:
            assert rule in rules
    assert after["permissions"]["deny"].count(existing_deny) == 1
    assert after["permissions"]["deny"][0] == existing_deny  # order preserved

    backups = list(cfg.glob("settings.json.launchpad-backup-*"))
    assert len(backups) == 1
    assert backups[0].read_bytes() == original_bytes


def test_apply_twice_is_a_noop_the_second_time(cfg):
    write(cfg / "settings.json", json.dumps({"model": "opus"}))
    assert doctor.apply_permissions()["applied"] is True
    path = cfg / "settings.json"
    first = path.read_bytes()
    assert doctor.apply_permissions()["applied"] is False
    assert path.read_bytes() == first


def test_apply_creates_missing_settings_without_backup(cfg):
    path = cfg / "settings.json"
    assert not path.exists()
    result = doctor.apply_permissions()
    assert result["applied"] is True
    assert result["backup"] is None
    data = json.loads(path.read_text(encoding="utf-8"))
    for kind, rules in doctor.RECOMMENDED.items():
        assert data["permissions"][kind] == rules
    assert doctor.missing_permissions() == ({}, None)


def test_apply_creates_config_dir_if_absent(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "fresh" / "cfg"))
    assert doctor.apply_permissions()["applied"] is True
    assert (tmp_path / "fresh" / "cfg" / "settings.json").is_file()


@pytest.mark.parametrize(
    "content",
    [
        '{"permissions": {"deny": "Read(x)"}}',
        '{"permissions": {"ask": {"a": 1}}}',
        '{"permissions": []}',
        '{"permissions": "nope"}',
        "{not json",
        "[1, 2]",
    ],
    ids=["deny-str", "ask-dict", "perm-list", "perm-str", "invalid-json", "json-list"],
)
def test_apply_refuses_unusable_settings_and_leaves_them_untouched(cfg, content):
    path = write(cfg / "settings.json", content)
    before = path.read_bytes()
    result = doctor.apply_permissions()
    assert result["applied"] is False
    assert result["error"]
    assert path.read_bytes() == before
    assert list(cfg.glob("settings.json.launchpad-backup-*")) == []


# --- fingerprint / record -----------------------------------------------------------


def test_record_writes_current_fingerprint(tmp_path):
    data_dir = tmp_path / "data"
    result = doctor.record(data_dir)
    entry = json.loads((data_dir / doctor.SETUP_RECORD).read_text(encoding="utf-8"))
    assert result["recorded"] is True
    assert entry["fingerprint"] == doctor.fingerprint()


def test_fingerprint_stable_when_nothing_changes(cfg):
    write(cfg / "CLAUDE.md", "rules")
    assert doctor.fingerprint() == doctor.fingerprint()


@pytest.mark.parametrize(
    "change",
    [
        lambda cfg: write(cfg / "CLAUDE.md", "changed"),
        lambda cfg: write(cfg / "settings.json", '{"disableAllHooks": true}'),
        lambda cfg: write(
            cfg / "settings.json",
            json.dumps({"permissions": {"deny": [doctor.RECOMMENDED["deny"][0]]}}),
        ),
        lambda cfg: write(cfg / "agents" / "new.md", "---\nname: new\n---\n"),
        lambda cfg: write(cfg / "skills" / "new" / "SKILL.md", "x"),
    ],
    ids=["claude-md", "hooks-off", "recommended-rule", "agent", "skill"],
)
def test_fingerprint_changes_with_user_config(cfg, change):
    write(cfg / "CLAUDE.md", "rules")
    before = doctor.fingerprint()
    change(cfg)
    assert doctor.fingerprint() != before


def test_fingerprint_ignores_unrelated_settings(cfg):
    """Claude Code rewrites settings.json for many reasons (model, theme, allow rules).
    Those must not trigger a re-run-setup nudge every session."""
    write(cfg / "settings.json", json.dumps({"model": "opus"}))
    before = doctor.fingerprint()
    write(cfg / "settings.json", json.dumps({"model": "sonnet", "theme": "dark"}, indent=4))
    assert doctor.fingerprint() == before


# --- main ---------------------------------------------------------------------------


def test_main_check_prints_valid_json(project, capsys):
    assert doctor.main(["check", "--project", str(project)]) == 0
    assert json.loads(capsys.readouterr().out)["missing_permissions"] == doctor.RECOMMENDED


def test_main_permissions_on_malformed_settings_returns_1(cfg, capsys):
    write(cfg / "settings.json", '{"permissions": []}')
    assert doctor.main(["permissions"]) == 1
    assert json.loads(capsys.readouterr().out)["error"]


def test_main_permissions_apply_on_malformed_settings_returns_1(cfg, capsys):
    path = write(cfg / "settings.json", "{broken")
    assert doctor.main(["permissions", "--apply"]) == 1
    assert path.read_text(encoding="utf-8") == "{broken"


# --- review regressions: settings write safety ---------------------------------------


def test_backup_keeps_the_private_mode_of_settings(cfg):
    """settings.json can hold tokens in `env`; its backup must not be more readable."""
    path = write(cfg / "settings.json", json.dumps({"env": {"TOKEN": "fabricated"}}))
    path.chmod(0o600)
    backup = Path(doctor.apply_permissions()["backup"])
    assert backup.stat().st_mode & 0o777 == 0o600
    assert path.stat().st_mode & 0o777 == 0o600


def test_backups_in_the_same_second_never_overwrite_each_other(cfg):
    path = write(cfg / "settings.json", "{}")
    first = doctor.backup_copy(path)
    path.write_text('{"changed": true}', encoding="utf-8")
    second = doctor.backup_copy(path)
    assert first != second
    assert first.read_text() == "{}"


def test_apply_leaves_no_temp_files_behind(cfg):
    write(cfg / "settings.json", "{}")
    doctor.apply_permissions()
    leftovers = [p.name for p in cfg.iterdir() if p.name.startswith(".settings.json.")]
    assert leftovers == []


def test_apply_writes_through_a_symlinked_settings_file(cfg, tmp_path):
    """Dotfile repos symlink settings.json; the link must survive the atomic rename."""
    real = write(tmp_path / "dotfiles" / "settings.json", json.dumps({"model": "opus"}))
    (cfg / "settings.json").symlink_to(real)
    doctor.apply_permissions()
    assert (cfg / "settings.json").is_symlink()
    assert "permissions" in json.loads(real.read_text(encoding="utf-8"))


def test_apply_keeps_non_ascii_readable(cfg):
    write(cfg / "settings.json", json.dumps({"note": "café"}, ensure_ascii=False))
    doctor.apply_permissions()
    assert "café" in (cfg / "settings.json").read_text(encoding="utf-8")


def test_settings_with_a_byte_order_mark_are_accepted(cfg):
    (cfg / "settings.json").write_bytes(b"\xef\xbb\xbf" + json.dumps({"model": "x"}).encode())
    assert doctor.check(cfg)["errors"] == []


def test_deeply_nested_settings_are_an_error_not_a_crash(cfg):
    write(cfg / "settings.json", "[" * 100_000 + "]" * 100_000)
    assert doctor.check(cfg)["errors"]


# --- review regressions: record and untrusted project files ---------------------------


@pytest.mark.parametrize("value", ["", "relative/dir"], ids=["empty", "relative"])
def test_record_refuses_a_missing_or_relative_data_dir(monkeypatch, tmp_path, value):
    """An unsubstituted ${CLAUDE_PLUGIN_DATA} arrives as "" — never write into cwd."""
    monkeypatch.chdir(tmp_path)
    assert doctor.main(["record", "--data-dir", value]) == 1
    assert not list(tmp_path.rglob(doctor.SETUP_RECORD))


def test_project_symlink_leading_outside_the_project_is_not_read(cfg, project, tmp_path):
    secret = write(tmp_path / "elsewhere" / "secret.txt", "fabricated secret")
    (project / "CLAUDE.md").symlink_to(secret)
    (project / ".claude" / "agents").mkdir(parents=True)
    (project / ".claude" / "agents" / "reviewer.md").symlink_to(secret)
    result = doctor.check(project)
    assert str(project / "CLAUDE.md") not in result["instruction_files"]
    assert result["name_overlaps"] == []


def test_symlinked_global_claude_md_is_still_read(cfg, tmp_path):
    """The user's own config dir is trusted: dotfile-repo links are normal there."""
    real = write(tmp_path / "dotfiles" / "CLAUDE.md", "my rules")
    (cfg / "CLAUDE.md").symlink_to(real)
    assert str(cfg / "CLAUDE.md") in doctor.check(tmp_path)["instruction_files"]


# --- audit regressions: user mistakes give a message, not a traceback -----------------


def test_apply_in_a_read_only_config_dir_reports_an_error(cfg):
    path = write(cfg / "settings.json", json.dumps({"model": "opus"}))
    original = path.read_bytes()
    cfg.chmod(0o500)
    try:
        result = doctor.apply_permissions()
    finally:
        cfg.chmod(0o700)
    assert result["applied"] is False and "left unchanged" in result["error"]
    assert path.read_bytes() == original
    assert [p.name for p in cfg.iterdir()] == ["settings.json"]  # no backup, no temp file


def test_record_onto_a_file_reports_an_error(tmp_path):
    blocker = write(tmp_path / "not-a-dir", "x")
    assert doctor.main(["record", "--data-dir", str(blocker)]) == 1


def test_unreadable_settings_get_a_non_json_hint(cfg):
    (cfg / "settings.json").mkdir()  # a directory where the file should be
    errors = doctor.check(cfg)["errors"]
    assert errors and "isn't valid JSON" not in errors[0]
