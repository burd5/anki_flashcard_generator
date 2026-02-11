import genanki


def get_kindle_clippings():
    pass


def filter_clippings():
    pass


def clear_clippings():
    pass


def main():
    my_deck = genanki.Deck(2059400110, "My Custom Deck")

    my_model = genanki.Model(
        1607392319,
        "Simple Model",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
        ],
        templates=[
            {
                "name": "Card 1",
                "qfmt": "{{Question}}",
                "afmt": '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ],
    )

    my_deck.add_note(genanki.Note(model=my_model, fields=["What is sodium nitrite?", "NaNO₂"]))

    genanki.Package(my_deck).write_to_file("my_deck.apkg")


if __name__ == "__main__":
    main()
