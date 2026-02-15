"""Tests for services/definition_api.py.

Mocks requests.get at the HTTP boundary.
"""

import pytest

from services.definition_api import get_word_definition


class _FakeResponse:
    """Typed stub for requests.Response -- avoids MagicMock."""

    def __init__(self, json_data: list | dict, status_code: int = 200) -> None:
        self._json_data = json_data
        self.status_code = status_code

    def json(self) -> list | dict:
        return self._json_data


def _dictionary_api_response(definition: str) -> list:
    return [
        {
            "meanings": [
                {
                    "definitions": [
                        {"definition": definition}
                    ]
                }
            ]
        }
    ]


class TestGetWordDefinition:

    def test_returns_definition_on_success(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake_response = _FakeResponse(
            _dictionary_api_response("lasting for a very short time")
        )
        monkeypatch.setattr("services.definition_api.requests.get", lambda url: fake_response)
        monkeypatch.setattr("services.definition_api.DICTIONARY_API_BASE_URL", "https://api.example.com/")

        result = get_word_definition("ephemeral")

        assert result == "lasting for a very short time"

    def test_returns_none_when_api_returns_empty_list(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake_response = _FakeResponse([])
        monkeypatch.setattr("services.definition_api.requests.get", lambda url: fake_response)
        monkeypatch.setattr("services.definition_api.DICTIONARY_API_BASE_URL", "https://api.example.com/")

        result = get_word_definition("xyznotaword")

        assert result is None

    def test_returns_none_when_api_returns_malformed_json(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        fake_response = _FakeResponse([{"no_meanings_key": []}])
        monkeypatch.setattr("services.definition_api.requests.get", lambda url: fake_response)
        monkeypatch.setattr("services.definition_api.DICTIONARY_API_BASE_URL", "https://api.example.com/")

        result = get_word_definition("test")

        assert result is None

    def test_returns_none_when_request_raises_exception(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def raise_connection_error(url):
            raise ConnectionError("network down")

        monkeypatch.setattr("services.definition_api.requests.get", raise_connection_error)
        monkeypatch.setattr("services.definition_api.DICTIONARY_API_BASE_URL", "https://api.example.com/")

        result = get_word_definition("test")

        assert result is None

    def test_constructs_url_from_base_url_and_word(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured_urls = []

        def capture_url(url):
            captured_urls.append(url)
            return _FakeResponse(_dictionary_api_response("a definition"))

        monkeypatch.setattr("services.definition_api.requests.get", capture_url)
        monkeypatch.setattr(
            "services.definition_api.DICTIONARY_API_BASE_URL",
            "https://api.example.com/define/",
        )

        get_word_definition("hello")

        assert captured_urls == ["https://api.example.com/define/hello"]
