from dotenv import load_dotenv
import uuid
from services.definition_api import get_word_definition
from models import Note

import os

load_dotenv()
CLIPPINGS_FILE = os.getenv("PATH_TO_CLIPPINGS_FILE", None)


def get_kindle_clippings_file() -> list[str]:
    """Grabs Kindle Clippings.txt file and parses highlights"""
    with open(CLIPPINGS_FILE) as f:
        notes_and_highlights = f.read().split("==========")
        highlights = [highlight for highlight in notes_and_highlights if "Highlight" in highlight]
        return highlights


def parse_highlights(highlights: list[str]) -> list[Note]:
    notes = []
    for highlight in highlights:
        text_and_author, highlighted_text = parse_highlight(highlight)
        card_front, card_back, deck_name = format_note(text_and_author, highlighted_text)
        if card_back == "":
            continue
        note = Note(
            deckName=deck_name,
            front=card_front,
            back=card_back,
        )
        notes.append(note)
    return notes


def parse_highlight(highlight: str) -> tuple[str, str]:
    lines = highlight.split("\n")
    title_and_author = lines[0] if lines[0] else lines[1]
    highlighted_text = lines[4]

    return title_and_author, highlighted_text


def format_note(title_and_author: str, highlighted_text: str) -> tuple[str, str, str]:
    # if highlighted text is single word, assume definition
    is_single_word = len(highlighted_text.split()) == 1
    # remove commas from single highlighted words
    if is_single_word:
        highlighted_text = highlighted_text.rstrip(",")
    card_back = get_word_definition(highlighted_text) if is_single_word else highlighted_text
    card_front = highlighted_text if is_single_word else highlighted_text
    deck_name = "Vocab" if is_single_word else title_and_author

    return card_front, card_back, deck_name
