from pydantic import BaseModel


class Note(BaseModel):
    deckName: str = "Default"
    modelName: str = "Basic"
    front: str
    back: str
    tags: list[str] = []
