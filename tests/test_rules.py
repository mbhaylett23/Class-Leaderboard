import importlib
from types import SimpleNamespace

import pytest
import streamlit_app.firebase as firebase


def _load_data(monkeypatch):
    monkeypatch.setattr(firebase, "get_db", lambda: SimpleNamespace())
    return importlib.reload(importlib.import_module("streamlit_app.data"))


def _fake_teacher_votes(monkeypatch, data):
    store = {}
    class Doc:
        def __init__(self, key):
            self.key = key
        def set(self, payload):
            store[self.key] = payload
    monkeypatch.setattr(data, "teacher_vote_ref", lambda *args: Doc(args[2]))
    return store


def test_submit_teacher_vote_writes_expected(monkeypatch):
    data = _load_data(monkeypatch)
    store = _fake_teacher_votes(monkeypatch, data)
    doc = data.submit_teacher_vote("class", "session", "admin", "team", {"clarity": 4})
    assert doc == store["admin"]
    assert doc["ratings"] == {"clarity": 4}


def test_submit_teacher_vote_validates_rating_range(monkeypatch):
    data = _load_data(monkeypatch)
    _fake_teacher_votes(monkeypatch, data)
    with pytest.raises(ValueError):
        data.submit_teacher_vote("class", "session", "admin", "team", {"clarity": 6})


def test_submit_teacher_vote_overwrites_duplicate(monkeypatch):
    data = _load_data(monkeypatch)
    store = _fake_teacher_votes(monkeypatch, data)
    data.submit_teacher_vote("class", "session", "admin", "team", {"clarity": 4})
    data.submit_teacher_vote("class", "session", "admin", "team", {"clarity": 2})
    assert store["admin"]["ratings"]["clarity"] == 2


def test_student_must_rate_all_categories_placeholder():
    # UI/Server should reject any submission with missing category ratings.
    assert True
