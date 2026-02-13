from dotenv import load_dotenv
from services.definition_api import get_word_definition
from models import Card, Model, Deck
from anki import add_card_to_deck
import os

load_dotenv()

CLIPPINGS_FILE = os.getenv("PATH_TO_CLIPPINGS_FILE", None)


def get_kindle_clippings_file():
    with open(CLIPPINGS_FILE) as f:
        notes_and_highlights = f.read().split("==========")
        highlights = [
            highlight for highlight in notes_and_highlights if "Highlight" in highlight
        ]
        # notes = [note for note in notes_and_highlights if "Note" in note]
        clip_highlights(highlights)


def clip_highlights(highlights):
    for highlight in highlights:
        lines = highlight.split("\n")
        title_and_author = lines[0] if lines[0] else lines[1]
        highlighted_text = lines[4]

        if len(highlighted_text.split()) == 1:
            deck = Deck("vocab")
            definition = get_word_definition(highlighted_text)
            card = Card(highlighted_text, definition)
            add_card_to_deck(deck, card)
        else:
            print(title_and_author)
            deck = Deck(deck_name=title_and_author)
            print(deck)
            model = Model(model_name="Simple Model")
            card = Card(question=highlighted_text, answer="")
            add_card_to_deck(deck, model, card)


def clear_clippings():
    pass


get_kindle_clippings_file()
