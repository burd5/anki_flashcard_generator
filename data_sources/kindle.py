from dotenv import load_dotenv
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
        high_text = lines[4]
        print(title_and_author, high_text)


def clear_clippings():
    pass


get_kindle_clippings_file()
