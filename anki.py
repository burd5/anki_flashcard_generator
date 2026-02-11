import genanki
from models import Deck, Card, Model


def add_card_to_deck(deck: Deck, model: Model, card: Card):
    return deck.add_note(genanki.Note(model=model, fields=[card.question, card.answer]))


def create_deck(deck_name: str):
    new_deck = Deck(deck_name=deck_name)
    return genanki.Deck(new_deck.anki_code, new_deck.deck_name)


def delete_card_from_deck():
    pass


def delete_deck():
    pass


def move_card_to_new_deck():
    pass
