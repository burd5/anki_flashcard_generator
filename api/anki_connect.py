import json
import os
import urllib.error
import urllib.request
from typing import Any

from api.exceptions import AnkiConnectError, AnkiConnectUnavailableError
from models.Note import Note

_DEFAULT_ANKI_CONNECT_URL = "http://127.0.0.1:8765"


def request(action: str, **params: Any) -> dict[str, Any]:
    return {"action": action, "params": params, "version": 6}


def invoke(action: str, **params: Any) -> Any:
    requestJson = json.dumps(request(action, **params)).encode("utf-8")
    url = os.environ.get("ANKI_CONNECT_URL", _DEFAULT_ANKI_CONNECT_URL)
    try:
        response = json.load(
            urllib.request.urlopen(
                urllib.request.Request(url, requestJson)
            )
        )
    except urllib.error.URLError:
        raise AnkiConnectUnavailableError("AnkiConnect is not reachable")
    if len(response) != 2:
        raise AnkiConnectError("response has an unexpected number of fields")
    if "error" not in response:
        raise AnkiConnectError("response is missing required error field")
    if "result" not in response:
        raise AnkiConnectError("response is missing required result field")
    if response["error"] is not None:
        raise AnkiConnectError(response["error"])
    return response["result"]


def deck_exists(deck_name: str) -> bool:
    decks = invoke("deckNames")
    return deck_name in decks


def create_deck(deck_name: str) -> int:
    return invoke("createDeck", deck=deck_name)


def add_note_to_deck(note: Note) -> int:
    if not deck_exists(note.deckName):
        create_deck(note.deckName)
    return invoke(
        "addNote",
        note={
            "deckName": note.deckName,
            "modelName": note.modelName,
            "fields": {"Front": note.front, "Back": note.back},
            "tags": note.tags,
        },
    )
