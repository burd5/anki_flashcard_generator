class AnkiConnectError(Exception):
    """AnkiConnect returned an error."""


class AnkiConnectUnavailableError(AnkiConnectError):
    """Cannot reach AnkiConnect."""
