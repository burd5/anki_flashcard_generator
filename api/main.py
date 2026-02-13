from fastapi import FastAPI
from anki_connect import create_deck, add_note_to_deck

app = FastAPI()


@app.post("/create_flashcard/{card}")
def add_card(card: str):
    add_note_to_deck(card)


@app.post("/create_deck/{deck}")
def add_deck(deck: str):
    create_deck(deck)
