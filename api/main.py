from fastapi import FastAPI
from fastapi.responses import JSONResponse
from http import HTTPStatus
from api.anki_connect import create_deck, add_note_to_deck
from api.exceptions import AnkiConnectError, AnkiConnectUnavailableError
from services.kindle import get_kindle_clippings_file, parse_highlights
from models.Note import Note

app = FastAPI()


@app.post("/create_flashcard")
def add_card(note: Note):
    try:
        note_id = add_note_to_deck(note)
        return JSONResponse(status_code=HTTPStatus.CREATED, content={"note_id": note_id})
    except AnkiConnectUnavailableError as e:
        return JSONResponse(status_code=HTTPStatus.BAD_GATEWAY, content={"error": str(e)})
    except AnkiConnectError as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": str(e)})


@app.post("/create_deck/{deck}")
def add_deck(deck: str):
    try:
        deck_id = create_deck(deck)
        return JSONResponse(status_code=HTTPStatus.CREATED, content={"deck_id": deck_id})
    except AnkiConnectUnavailableError as e:
        return JSONResponse(status_code=HTTPStatus.BAD_GATEWAY, content={"error": str(e)})
    except AnkiConnectError as e:
        return JSONResponse(status_code=HTTPStatus.BAD_REQUEST, content={"error": str(e)})


@app.post("/process_kindle_clippings")
def process_kindle_clippings():
    try:
        highlights = get_kindle_clippings_file()
        notes = parse_highlights(highlights)
    except Exception as e:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content={"error": f"Failed to process clippings: {e}"},
        )
    created = 0
    errors = []
    for note in notes:
        try:
            add_note_to_deck(note)
            created += 1
        except AnkiConnectUnavailableError as e:
            return JSONResponse(status_code=HTTPStatus.BAD_GATEWAY, content={"error": str(e)})
        except AnkiConnectError as e:
            errors.append((note.__dict__, str(e)))
    status = HTTPStatus.CREATED if created > 0 else HTTPStatus.BAD_REQUEST
    return JSONResponse(
        status_code=status,
        content={"created": created, "failed": len(errors), "errors": errors},
    )
