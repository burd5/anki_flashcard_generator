from dotenv import load_dotenv
import uuid
import pprint
from services.definition_api import get_word_definition
from models import Note
import requests
import os

load_dotenv()

CLIPPINGS_FILE = os.getenv("PATH_TO_CLIPPINGS_FILE", None)


def get_kindle_clippings_file():
    with open(CLIPPINGS_FILE) as f:
        notes_and_highlights = f.read().split("==========")
        highlights = [highlight for highlight in notes_and_highlights if "Highlight" in highlight]
        # notes = [note for note in notes_and_highlights if "Note" in note]
        return highlights


def clip_highlights(highlights):
    for highlight in highlights:
        lines = highlight.split("\n")
        title_and_author = lines[0] if lines[0] else lines[1]
        highlighted_text = lines[4]
        # if highlighted text is single word, assume definition
        is_single_word = len(highlighted_text.split()) == 1
        card_back = get_word_definition(highlighted_text) if is_single_word else highlighted_text
        card_front = highlighted_text if is_single_word else str(uuid.uuid4())
        deck_name = "Vocab" if is_single_word else title_and_author
        note = Note(
            deckName=deck_name,
            front=card_front,
            back=card_back,
        )
        pprint.pp(note.__dict__)
        response = requests.post("http://127.0.0.1:8000/create_flashcard", json=note.model_dump())
