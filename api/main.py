from fastapi import FastAPI
from api.anki_connect import create_deck, add_note_to_deck
from services.kindle import get_kindle_clippings_file, clip_highlights
from models.Note import Note

app = FastAPI()


@app.post("/create_flashcard")
def add_card(note: Note):
    add_note_to_deck(note)


@app.post("/create_deck/{deck}")
def add_deck(deck: str):
    create_deck(deck)


@app.post("/process_clippings")
def process_kindle_clippings():
    highlights = get_kindle_clippings_file()
    clip_highlights(highlights)
