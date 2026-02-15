import pytest

from models.Note import Note


@pytest.fixture()
def sample_note() -> Note:
    return Note(
        deckName="TestDeck",
        modelName="Basic",
        front="test front",
        back="test back",
        tags=["test"],
    )


@pytest.fixture()
def sample_note_default() -> Note:
    return Note(front="front text", back="back text")


KINDLE_HIGHLIGHT_SINGLE_WORD = (
    "\nThe Great Gatsby (F. Scott Fitzgerald)\n"
    "- Your Highlight on page 42 | Added on Monday\n"
    "\n"
    "ephemeral\n"
)

KINDLE_HIGHLIGHT_PASSAGE = (
    "\nSapiens (Yuval Noah Harari)\n"
    "- Your Highlight on page 100 | Added on Tuesday\n"
    "\n"
    "History began when humans invented gods\n"
)

KINDLE_HIGHLIGHT_SINGLE_WORD_WITH_COMMA = (
    "\nThe Great Gatsby (F. Scott Fitzgerald)\n"
    "- Your Highlight on page 42 | Added on Monday\n"
    "\n"
    "ephemeral,\n"
)

KINDLE_CLIPPINGS_RAW = (
    KINDLE_HIGHLIGHT_SINGLE_WORD
    + "=========="
    + KINDLE_HIGHLIGHT_PASSAGE
    + "=========="
    + "\nSome Book (Author)\n- Your Bookmark on page 5 | Added on Friday\n\n\n"
)


@pytest.fixture()
def kindle_highlight_single_word() -> str:
    return KINDLE_HIGHLIGHT_SINGLE_WORD


@pytest.fixture()
def kindle_highlight_passage() -> str:
    return KINDLE_HIGHLIGHT_PASSAGE


@pytest.fixture()
def kindle_highlight_single_word_with_comma() -> str:
    return KINDLE_HIGHLIGHT_SINGLE_WORD_WITH_COMMA


@pytest.fixture()
def kindle_clippings_raw() -> str:
    return KINDLE_CLIPPINGS_RAW
