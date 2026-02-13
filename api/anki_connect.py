from http import HTTPStatus
from models.Note import Note
import json
import urllib.request


def request(action, **params):
    return {"action": action, "params": params, "version": 6}


def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode("utf-8")
    response = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8765", requestJson)))
    if len(response) != 2:
        raise Exception("response has an unexpected number of fields")
    if "error" not in response:
        raise Exception("response is missing required error field")
    if "result" not in response:
        raise Exception("response is missing required result field")
    if response["error"] is not None:
        raise Exception(response["error"])
    return response["result"]


def deck_exists(deck_name: str) -> bool:
    decks = invoke("deckNames")
    return deck_name in decks


def create_deck(deck_name: str) -> HTTPStatus:
    exists = deck_exists(deck_name)
    try:
        if not exists:
            invoke("createDeck", deck=deck_name)
            return HTTPStatus.OK
        return HTTPStatus.BAD_REQUEST
    except Exception:
        return HTTPStatus.BAD_REQUEST


def add_note_to_deck(note: Note) -> HTTPStatus:
    response = invoke(
        "addNote",
        note={
            "deckName": note.deckName,
            "modelName": note.modelName,
            "fields": {"Front": note.front, "Back": note.back},
            "tags": note.tags,
        },
    )
    if response:
        return HTTPStatus.OK
