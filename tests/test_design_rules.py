"""Design-rule preservation: rewording a design skill must not change its rules.

The design skills' value is their concrete rules — contrast ratios, spacing scales,
hit-target sizes, timings, the CSS and HTML identifiers they prescribe. This test
compares each file against a frozen snapshot of those tokens
(`fixtures/design_rules.json`) and fails if any token disappears.

Limits: tokens are compared as a set per file, so a value that also appears
elsewhere in the same file is not pinned to each use. Meaning ("must" vs
"should") is checked by a reviewer reading old against new, not here.

Catastrophic failure mode pinned: a rewrite silently drops or alters a number
(e.g. a 4.5:1 contrast minimum becoming 4:1, or a 44px target vanishing).

To change a rule on purpose, edit the skill, then regenerate the snapshot and review
its diff:  uv run python tests/test_design_rules.py --write
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = Path(__file__).resolve().parent / "fixtures" / "design_rules.json"

FILES = [
    "skills/accessibility-audit/SKILL.md",
    "skills/component-extract/SKILL.md",
    "skills/design-system-extract/SKILL.md",
    "skills/generate-variations/SKILL.md",
    "skills/make-a-deck/SKILL.md",
    "skills/make-a-prototype/SKILL.md",
    "skills/make-tweakable/SKILL.md",
    "skills/polish-pass/SKILL.md",
    "skills/wireframe/SKILL.md",
    "skills/design/references/a11y.md",
    "skills/design/references/design-tokens.md",
]

# Ordered-list markers ("1. ") and markdown heading levels are structure, not rules.
LIST_MARKER = re.compile(r"^\s*\d+\.\s", re.MULTILINE)
# A value with optional ratio/range/dimension parts and an optional unit:
# 4.5:1, 44px, 200–300ms, 1920×1080, 16:9, 1.5, 8px, 100%.
VALUE = re.compile(
    r"(?<![\w.#-])\d+(?:\.\d+)?(?:\s?[:×x/–-]\s?\d+(?:\.\d+)?)*"
    # Ends at anything but a word character or a decimal point; a full stop that
    # ends the sentence ("at least 44px.") must not cancel the match.
    r"(?:px|ms|rem|em|vh|vw|pt|s|%|deg|ch|fr|dp)?(?!\w|\.\d)"
)
CODE = re.compile(r"`([^`\n]+)`")


def tokens(text: str) -> dict[str, list[str]]:
    """The rule-bearing tokens in a file: numeric values and inline code spans."""
    text = LIST_MARKER.sub("", text)
    values = {re.sub(r"\s+", "", v) for v in VALUE.findall(text)}
    code = set(CODE.findall(text))
    return {"values": sorted(values), "code": sorted(code)}


def write_snapshot() -> None:
    snapshot = {f: tokens((ROOT / f).read_text(encoding="utf-8")) for f in FILES}
    SNAPSHOT.parent.mkdir(exist_ok=True)
    SNAPSHOT.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")


def load_snapshot() -> dict[str, dict[str, list[str]]]:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", FILES)
def test_every_rule_token_survives(path: str) -> None:
    expected = load_snapshot()[path]
    current = tokens((ROOT / path).read_text(encoding="utf-8"))
    missing_values = sorted(set(expected["values"]) - set(current["values"]))
    missing_code = sorted(set(expected["code"]) - set(current["code"]))
    assert not missing_values, f"{path} lost values: {missing_values}"
    assert not missing_code, f"{path} lost code identifiers: {missing_code}"


def test_snapshot_covers_exactly_the_rewritten_files() -> None:
    assert sorted(load_snapshot()) == sorted(FILES)


@pytest.mark.parametrize(
    ("text", "value"),
    [
        ("Body text needs 4.5:1 contrast.", "4.5:1"),
        ("Targets at least 44px.", "44px"),
        ("Transitions take 200–300ms.", "200–300ms"),
        ("A 1920×1080 canvas.", "1920×1080"),
        ("Use 16:9 slides.", "16:9"),
    ],
)
def test_extractor_finds_rule_values(text: str, value: str) -> None:
    assert value in tokens(text)["values"]


def test_extractor_ignores_list_markers() -> None:
    assert tokens("1. First\n2. Second\n")["values"] == []


if __name__ == "__main__" and "--write" in sys.argv:
    write_snapshot()
    print(f"wrote {SNAPSHOT.relative_to(ROOT)}")
