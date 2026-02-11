from pydantic import BaseModel


class Deck(BaseModel):
    deck_name: str
    anki_code: int = 2059400110
