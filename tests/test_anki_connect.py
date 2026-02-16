"""Tests for api/anki_connect.py.

Mocks urllib.request.urlopen at the network boundary to test
invoke() validation logic and higher-level functions.
"""

import io
import json
import urllib.error

import pytest

from api.anki_connect import (
    add_note_to_deck,
    create_deck,
    deck_exists,
    invoke,
    request,
)
from api.exceptions import AnkiConnectError, AnkiConnectUnavailableError
from models.Note import Note


def _fake_urlopen(response_dict: dict):
    """Return a callable that simulates urlopen returning a JSON response."""
    def fake(req):
        data = json.dumps(response_dict).encode("utf-8")
        return io.BytesIO(data)
    return fake


def _fake_urlopen_raising_urlerror(req):
    raise urllib.error.URLError("connection refused")


class TestRequest:
    """Pure function -- no mocking needed (Level 0)."""

    def test_builds_request_dict_with_action_and_version(self) -> None:
        result = request("deckNames")

        assert result == {"action": "deckNames", "params": {}, "version": 6}

    def test_builds_request_dict_with_params(self) -> None:
        result = request("createDeck", deck="MyDeck")

        assert result == {
            "action": "createDeck",
            "params": {"deck": "MyDeck"},
            "version": 6,
        }


class TestInvoke:

    def test_returns_result_on_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "urllib.request.urlopen",
            _fake_urlopen({"result": ["Default", "Vocab"], "error": None}),
        )

        result = invoke("deckNames")

        assert result == ["Default", "Vocab"]

    def test_raises_unavailable_error_on_url_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "urllib.request.urlopen", _fake_urlopen_raising_urlerror
        )

        with pytest.raises(AnkiConnectUnavailableError, match="not reachable"):
            invoke("deckNames")

    def test_raises_error_when_response_has_unexpected_field_count(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "urllib.request.urlopen",
            _fake_urlopen({"result": None, "error": None, "extra": "field"}),
        )

        with pytest.raises(AnkiConnectError, match="unexpected number of fields"):
            invoke("deckNames")

    def test_raises_error_when_response_missing_error_field(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "urllib.request.urlopen",
            _fake_urlopen({"result": None, "other": None}),
        )

        with pytest.raises(AnkiConnectError, match="missing required error field"):
            invoke("deckNames")

    def test_raises_error_when_response_missing_result_field(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "urllib.request.urlopen",
            _fake_urlopen({"error": None, "other": None}),
        )

        with pytest.raises(AnkiConnectError, match="missing required result field"):
            invoke("deckNames")

    def test_raises_error_when_response_error_is_not_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "urllib.request.urlopen",
            _fake_urlopen({"result": None, "error": "model not found"}),
        )

        with pytest.raises(AnkiConnectError, match="model not found"):
            invoke("deckNames")


class TestDeckExists:

    def test_returns_true_when_deck_in_list(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "api.anki_connect.invoke",
            lambda action, **kw: ["Default", "Vocab", "MyDeck"],
        )

        assert deck_exists("MyDeck") is True

    def test_returns_false_when_deck_not_in_list(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "api.anki_connect.invoke",
            lambda action, **kw: ["Default", "Vocab"],
        )

        assert deck_exists("NonExistent") is False


class TestCreateDeck:

    def test_returns_deck_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "api.anki_connect.invoke", lambda action, **kw: 1234567890
        )

        result = create_deck("NewDeck")

        assert result == 1234567890


class TestAddNoteToDeck:

    def test_creates_deck_when_it_does_not_exist(
        self, monkeypatch: pytest.MonkeyPatch, sample_note: Note
    ) -> None:
        created_decks = []

        monkeypatch.setattr(
            "api.anki_connect.deck_exists", lambda name: False
        )
        monkeypatch.setattr(
            "api.anki_connect.create_deck",
            lambda name: created_decks.append(name) or 1,
        )
        monkeypatch.setattr(
            "api.anki_connect.invoke", lambda action, **kw: 42
        )

        add_note_to_deck(sample_note)

        assert created_decks == ["TestDeck"]

    def test_skips_deck_creation_when_deck_exists(
        self, monkeypatch: pytest.MonkeyPatch, sample_note: Note
    ) -> None:
        created_decks = []

        monkeypatch.setattr(
            "api.anki_connect.deck_exists", lambda name: True
        )
        monkeypatch.setattr(
            "api.anki_connect.create_deck",
            lambda name: created_decks.append(name) or 1,
        )
        monkeypatch.setattr(
            "api.anki_connect.invoke", lambda action, **kw: 42
        )

        add_note_to_deck(sample_note)

        assert created_decks == []

    def test_returns_note_id(
        self, monkeypatch: pytest.MonkeyPatch, sample_note: Note
    ) -> None:
        monkeypatch.setattr(
            "api.anki_connect.deck_exists", lambda name: True
        )
        monkeypatch.setattr(
            "api.anki_connect.invoke", lambda action, **kw: 99999
        )

        result = add_note_to_deck(sample_note)

        assert result == 99999

    def test_passes_correct_note_structure_to_invoke(
        self, monkeypatch: pytest.MonkeyPatch, sample_note: Note
    ) -> None:
        captured_kwargs = {}

        def capture_invoke(action, **kwargs):
            captured_kwargs.update(kwargs)
            return 1

        monkeypatch.setattr("api.anki_connect.deck_exists", lambda name: True)
        monkeypatch.setattr("api.anki_connect.invoke", capture_invoke)

        add_note_to_deck(sample_note)

        expected_note = {
            "deckName": "TestDeck",
            "modelName": "Basic",
            "fields": {"Front": "test front", "Back": "test back"},
            "tags": ["test"],
        }
        assert captured_kwargs["note"] == expected_note


class TestAnkiConnectUrl:

    def test_default_anki_connect_url(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ANKI_CONNECT_URL", raising=False)

        captured_requests = []

        def capture_urlopen(req):
            captured_requests.append(req)
            data = json.dumps({"result": None, "error": None}).encode("utf-8")
            return io.BytesIO(data)

        monkeypatch.setattr("urllib.request.urlopen", capture_urlopen)

        invoke("deckNames")

        assert len(captured_requests) == 1
        assert captured_requests[0].full_url == "http://127.0.0.1:8765"

    def test_invoke_uses_custom_url_from_env(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        custom_url = "http://custom:9999"
        monkeypatch.setenv("ANKI_CONNECT_URL", custom_url)

        captured_requests = []

        def capture_urlopen(req):
            captured_requests.append(req)
            data = json.dumps({"result": None, "error": None}).encode("utf-8")
            return io.BytesIO(data)

        monkeypatch.setattr("urllib.request.urlopen", capture_urlopen)

        invoke("deckNames")

        assert len(captured_requests) == 1
        assert captured_requests[0].full_url == custom_url
