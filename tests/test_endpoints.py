"""Integration tests for FastAPI endpoints.

Mocks the service layer (anki_connect, kindle) to test HTTP behavior:
status codes, response bodies, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from http import HTTPStatus

from api.main import app
from api.exceptions import AnkiConnectError, AnkiConnectUnavailableError


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


class TestHealthzEndpoint:

    def test_returns_200_with_status_ok(self, client: TestClient) -> None:
        response = client.get("/healthz")

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"status": "ok"}


class TestCreateFlashcardEndpoint:

    def test_returns_201_with_note_id_on_success(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "api.main.add_note_to_deck", lambda note: 12345
        )

        response = client.post(
            "/create_flashcard",
            json={"front": "hello", "back": "world"},
        )

        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {"note_id": 12345}

    def test_returns_502_when_anki_connect_unavailable(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def raise_unavailable(note):
            raise AnkiConnectUnavailableError("AnkiConnect is not reachable")

        monkeypatch.setattr("api.main.add_note_to_deck", raise_unavailable)

        response = client.post(
            "/create_flashcard",
            json={"front": "hello", "back": "world"},
        )

        assert response.status_code == HTTPStatus.BAD_GATEWAY
        assert response.json() == {"error": "AnkiConnect is not reachable"}

    def test_returns_400_on_anki_connect_error(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def raise_error(note):
            raise AnkiConnectError("duplicate note")

        monkeypatch.setattr("api.main.add_note_to_deck", raise_error)

        response = client.post(
            "/create_flashcard",
            json={"front": "hello", "back": "world"},
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {"error": "duplicate note"}

    def test_returns_422_when_missing_required_fields(
        self, client: TestClient
    ) -> None:
        response = client.post("/create_flashcard", json={})

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_uses_default_deck_and_model_when_not_provided(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured = {}

        def capture_note(note):
            captured["deckName"] = note.deckName
            captured["modelName"] = note.modelName
            return 1

        monkeypatch.setattr("api.main.add_note_to_deck", capture_note)

        response = client.post(
            "/create_flashcard",
            json={"front": "hello", "back": "world"},
        )

        assert response.status_code == HTTPStatus.CREATED
        assert captured["deckName"] == "Default"
        assert captured["modelName"] == "Basic"


class TestCreateDeckEndpoint:

    def test_returns_201_with_deck_id_on_success(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("api.main.create_deck", lambda deck: 99)

        response = client.post("/create_deck/MyDeck")

        assert response.status_code == HTTPStatus.CREATED
        assert response.json() == {"deck_id": 99}

    def test_returns_502_when_anki_connect_unavailable(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def raise_unavailable(deck):
            raise AnkiConnectUnavailableError("AnkiConnect is not reachable")

        monkeypatch.setattr("api.main.create_deck", raise_unavailable)

        response = client.post("/create_deck/MyDeck")

        assert response.status_code == HTTPStatus.BAD_GATEWAY
        assert response.json() == {"error": "AnkiConnect is not reachable"}

    def test_returns_400_on_anki_connect_error(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def raise_error(deck):
            raise AnkiConnectError("deck already exists")

        monkeypatch.setattr("api.main.create_deck", raise_error)

        response = client.post("/create_deck/MyDeck")

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert response.json() == {"error": "deck already exists"}


class TestProcessKindleClippingsEndpoint:

    def test_returns_201_with_created_count_on_success(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from models.Note import Note

        fake_notes = [
            Note(front="word1", back="def1", deckName="Vocab"),
            Note(front="word2", back="def2", deckName="Vocab"),
        ]
        monkeypatch.setattr("api.main.get_kindle_clippings_file", lambda: ["h1", "h2"])
        monkeypatch.setattr("api.main.parse_highlights", lambda h: fake_notes)
        monkeypatch.setattr("api.main.add_note_to_deck", lambda note: 1)

        response = client.post("/process_kindle_clippings")

        assert response.status_code == HTTPStatus.CREATED
        body = response.json()
        assert body["created"] == 2
        assert body["failed"] == 0
        assert body["errors"] == []

    def test_returns_502_when_anki_connect_unavailable_during_processing(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from models.Note import Note

        fake_notes = [Note(front="word1", back="def1")]
        monkeypatch.setattr("api.main.get_kindle_clippings_file", lambda: ["h1"])
        monkeypatch.setattr("api.main.parse_highlights", lambda h: fake_notes)

        def raise_unavailable(note):
            raise AnkiConnectUnavailableError("AnkiConnect is not reachable")

        monkeypatch.setattr("api.main.add_note_to_deck", raise_unavailable)

        response = client.post("/process_kindle_clippings")

        assert response.status_code == HTTPStatus.BAD_GATEWAY
        assert response.json() == {"error": "AnkiConnect is not reachable"}

    def test_collects_errors_for_failed_notes_and_continues(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from models.Note import Note

        fake_notes = [
            Note(front="word1", back="def1"),
            Note(front="word2", back="def2"),
            Note(front="word3", back="def3"),
        ]
        monkeypatch.setattr("api.main.get_kindle_clippings_file", lambda: ["h1"])
        monkeypatch.setattr("api.main.parse_highlights", lambda h: fake_notes)

        call_count = 0

        def succeed_then_fail(note):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise AnkiConnectError("duplicate note")
            return call_count

        monkeypatch.setattr("api.main.add_note_to_deck", succeed_then_fail)

        response = client.post("/process_kindle_clippings")

        assert response.status_code == HTTPStatus.CREATED
        body = response.json()
        assert body["created"] == 2
        assert body["failed"] == 1
        assert body["errors"] == ["duplicate note"]
