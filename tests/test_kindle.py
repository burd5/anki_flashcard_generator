"""Tests for services/kindle.py.

Tests parse_highlight and format_note as pure logic (Level 0).
Mocks file I/O for get_kindle_clippings_file and the definition API
dependency in format_note.
"""

import pytest

from models.Note import Note
from services.kindle import (
    format_note,
    get_kindle_clippings_file,
    parse_highlight,
    parse_highlights,
)


class TestParseHighlight:
    """Pure parsing logic -- no mocking needed."""

    def test_extracts_title_and_highlighted_text(
        self, kindle_highlight_single_word: str
    ) -> None:
        title, text = parse_highlight(kindle_highlight_single_word)

        assert title == "The Great Gatsby (F. Scott Fitzgerald)"
        assert text == "ephemeral"

    def test_extracts_passage_text(
        self, kindle_highlight_passage: str
    ) -> None:
        title, text = parse_highlight(kindle_highlight_passage)

        assert title == "Sapiens (Yuval Noah Harari)"
        assert text == "History began when humans invented gods"

    def test_handles_leading_empty_line_by_using_second_line(self) -> None:
        highlight = "\nBook Title (Author)\n- Your Highlight on page 1 | Added on Monday\n\nsome text\n"

        title, text = parse_highlight(highlight)

        assert title == "Book Title (Author)"
        assert text == "some text"


class TestFormatNote:

    def test_single_word_uses_vocab_deck(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "services.kindle.get_word_definition",
            lambda word: "lasting for a short time",
        )

        front, back, deck = format_note(
            "The Great Gatsby (F. Scott Fitzgerald)", "ephemeral"
        )

        assert deck == "Vocab"
        assert front == "ephemeral"
        assert back == "lasting for a short time"

    def test_single_word_strips_trailing_comma(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured_words = []

        def capture_word(word):
            captured_words.append(word)
            return "a definition"

        monkeypatch.setattr(
            "services.kindle.get_word_definition", capture_word
        )

        front, back, deck = format_note("Book (Author)", "ephemeral,")

        assert captured_words == ["ephemeral"]
        assert front == "ephemeral"

    def test_passage_uses_book_title_as_deck(self) -> None:
        front, back, deck = format_note(
            "Sapiens (Yuval Noah Harari)",
            "History began when humans invented gods",
        )

        assert deck == "Sapiens (Yuval Noah Harari)"
        assert back == "History began when humans invented gods"

    def test_passage_front_equals_highlighted_text(self) -> None:
        front, _back, _deck = format_note(
            "Sapiens (Yuval Noah Harari)",
            "History began when humans invented gods",
        )

        assert front == "History began when humans invented gods"

    def test_single_word_with_none_definition(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            "services.kindle.get_word_definition", lambda word: None
        )

        front, back, deck = format_note("Book (Author)", "xyznotaword")

        assert front == "xyznotaword"
        assert back is None
        assert deck == "Vocab"


class TestParseHighlights:

    def test_returns_list_of_notes(
        self, monkeypatch: pytest.MonkeyPatch,
        kindle_highlight_single_word: str,
        kindle_highlight_passage: str,
    ) -> None:
        monkeypatch.setattr(
            "services.kindle.get_word_definition",
            lambda word: "a definition",
        )
        highlights = [kindle_highlight_single_word, kindle_highlight_passage]

        notes = parse_highlights(highlights)

        assert len(notes) == 2
        assert all(isinstance(n, Note) for n in notes)

    def test_single_word_highlight_becomes_vocab_note(
        self, monkeypatch: pytest.MonkeyPatch,
        kindle_highlight_single_word: str,
    ) -> None:
        monkeypatch.setattr(
            "services.kindle.get_word_definition",
            lambda word: "lasting for a short time",
        )

        notes = parse_highlights([kindle_highlight_single_word])

        note = notes[0]
        assert note.deckName == "Vocab"
        assert note.front == "ephemeral"
        assert note.back == "lasting for a short time"

    def test_passage_highlight_becomes_book_titled_note(
        self, kindle_highlight_passage: str,
    ) -> None:
        notes = parse_highlights([kindle_highlight_passage])

        note = notes[0]
        assert note.deckName == "Sapiens (Yuval Noah Harari)"
        assert note.back == "History began when humans invented gods"

    def test_empty_highlights_returns_empty_list(self) -> None:
        notes = parse_highlights([])

        assert notes == []


class TestGetKindleClippingsFile:

    def test_reads_and_splits_clippings_file(
        self, monkeypatch: pytest.MonkeyPatch, kindle_clippings_raw: str
    ) -> None:
        monkeypatch.setattr(
            "services.kindle.CLIPPINGS_FILE", "/fake/path.txt"
        )
        monkeypatch.setattr(
            "builtins.open",
            lambda path, *a, **kw: _FakeFile(kindle_clippings_raw),
        )

        highlights = get_kindle_clippings_file()

        # Only entries containing "Highlight" are returned; bookmarks are excluded
        assert len(highlights) == 2
        assert all("Highlight" in h for h in highlights)

    def test_excludes_bookmarks(
        self, monkeypatch: pytest.MonkeyPatch, kindle_clippings_raw: str
    ) -> None:
        monkeypatch.setattr(
            "services.kindle.CLIPPINGS_FILE", "/fake/path.txt"
        )
        monkeypatch.setattr(
            "builtins.open",
            lambda path, *a, **kw: _FakeFile(kindle_clippings_raw),
        )

        highlights = get_kindle_clippings_file()

        assert not any("Bookmark" in h for h in highlights)


class _FakeFile:
    """Stub for file I/O -- supports context manager protocol."""

    def __init__(self, content: str) -> None:
        self._content = content

    def read(self) -> str:
        return self._content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
