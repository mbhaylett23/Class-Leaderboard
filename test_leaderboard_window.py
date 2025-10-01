"""Ad-hoc tests for the Streamlit leaderboard projection view."""
from __future__ import annotations

import types
from typing import List

import pytest

from streamlit_app import app
from streamlit_app import ui_leaderboard as leaderboard


class _FakeQueryParams(dict):
    """Minimal stand-in for Streamlit's QueryParams mapping."""

    def pop(self, key, default=None):
        return super().pop(key, default)


def _no_op(*args, **kwargs) -> None:
    """Shared stub that ignores Streamlit UI calls during tests."""
    return None


def test_get_query_param_reads_streamlit_state(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_params = _FakeQueryParams({"session": ["abc"], "view": ["leaderboard"]})
    monkeypatch.setattr(leaderboard.st, "query_params", fake_params, raising=False)
    assert leaderboard._get_query_param("view") == "leaderboard"
    assert leaderboard._get_query_param("missing") is None


def test_main_bypasses_auth_for_leaderboard(monkeypatch: pytest.MonkeyPatch) -> None:
    invoked = {"leaderboard": False}
    fake_params = _FakeQueryParams({"view": "leaderboard"})
    monkeypatch.setattr(app.st, "query_params", fake_params, raising=False)
    monkeypatch.setattr(app.st, "title", _no_op)
    monkeypatch.setattr(app.st, "sidebar", types.SimpleNamespace(radio=lambda *args, **kwargs: "Student", button=lambda *a, **k: False))
    monkeypatch.setattr(app.st, "session_state", {})
    monkeypatch.setattr(app.st, "rerun", _no_op)
    monkeypatch.setattr(app.st, "caption", _no_op)
    monkeypatch.setattr(app.st, "tabs", lambda labels: [types.SimpleNamespace(__enter__=lambda self: None, __exit__=lambda self, exc_type, exc, tb: None) for _ in labels])
    monkeypatch.setattr(
        app,
        "leaderboard_view",
        lambda role="student": invoked.__setitem__("leaderboard", True),
    )
    monkeypatch.setattr(app.st, "stop", lambda: (_ for _ in ()).throw(RuntimeError("stop")))

    with pytest.raises(RuntimeError):
        app.main()
    assert invoked["leaderboard"] is True


def test_leaderboard_refresh_uses_five_second_interval(monkeypatch: pytest.MonkeyPatch) -> None:
    sleep_calls: List[float] = []
    monkeypatch.setattr(leaderboard.time, "sleep", lambda seconds: sleep_calls.append(seconds))
    monkeypatch.setattr(leaderboard.st, "rerun", lambda: (_ for _ in ()).throw(RuntimeError("rerun")), raising=False)
    monkeypatch.setattr(leaderboard.st, "warning", _no_op)
    monkeypatch.setattr(leaderboard.st, "markdown", _no_op)
    monkeypatch.setattr(leaderboard.data, "list_classes", lambda: [])
    monkeypatch.setattr(leaderboard.st, "query_params", _FakeQueryParams({}), raising=False)

    with pytest.raises(RuntimeError):
        leaderboard.leaderboard_view()
    assert sleep_calls == [leaderboard.REFRESH_SECONDS]
    assert leaderboard.REFRESH_SECONDS == 5


def test_update_query_params_persists_existing_values(monkeypatch: pytest.MonkeyPatch) -> None:
    params = _FakeQueryParams({"view": "leaderboard", "class": "c1"})
    monkeypatch.setattr(leaderboard.st, "query_params", params, raising=False)

    leaderboard._update_query_params(session="s2")
    assert dict(params) == {"view": "leaderboard", "class": "c1", "session": "s2"}

    leaderboard._update_query_params(session=None)
    assert dict(params) == {"view": "leaderboard", "class": "c1"}
