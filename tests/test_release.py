from types import SimpleNamespace
import subprocess

from core import release


def test_build_metadata(monkeypatch):
    monkeypatch.setenv("JALA_BUILD_COMMIT", "ABCDEF123456")
    assert release.build_identity() == "Commit build: abcdef1 (metadata deployment)"


def test_dirty_checkout_is_explicit(monkeypatch):
    monkeypatch.delenv("JALA_BUILD_COMMIT", raising=False)
    results = iter([SimpleNamespace(stdout="a" * 40), SimpleNamespace(stdout=" M app.py")])
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: next(results))
    assert "bukan salinan persis commit" in release.build_identity()


def test_clean_checkout(monkeypatch):
    monkeypatch.delenv("JALA_BUILD_COMMIT", raising=False)
    results = iter([SimpleNamespace(stdout="b" * 40), SimpleNamespace(stdout="")])
    monkeypatch.setattr(subprocess, "run", lambda *a, **kw: next(results))
    assert release.build_identity() == "Commit checkout: bbbbbbb"


def test_missing_git_and_invalid_metadata(monkeypatch):
    monkeypatch.setenv("JALA_BUILD_COMMIT", "not-a-sha")
    def unavailable(*args, **kwargs):
        raise FileNotFoundError("git")
    monkeypatch.setattr(subprocess, "run", unavailable)
    assert release.build_identity() == "Commit tidak tersedia"
