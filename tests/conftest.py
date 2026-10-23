"""Shared test setup."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def hermetic_git(monkeypatch, tmp_path_factory):
    """Run every git command in the tests with an empty global and system config.

    Tests create throwaway repos and commit fabricated secrets on purpose. A
    developer's own git config (a global pre-commit hook, commit signing, a
    diff driver) would otherwise apply to those commits and change the results.
    """
    empty = tmp_path_factory.mktemp("gitconfig") / "config"
    empty.write_text("", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
