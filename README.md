# AnkiHandler

A FastAPI service for programmatically creating Anki flashcards via AnkiConnect. Designed to run on a Raspberry Pi as a central API for multiple data sources 

## Overview

AnkiHandler provides a REST API that communicates with a running Anki instance through the AnkiConnect plugin. It eliminates the need for manual `.apkg` file generation by directly creating decks and cards in real-time.

**Key features:**
- Create individual flashcards programmatically
- Batch-process Kindle highlights into vocabulary flashcards
- Automatic word definition lookup for single-word highlights

## Prerequisites

- Python 3.12+
- Anki desktop application with [AnkiConnect](https://ankiweb.net/shared/info/2055492159) plugin installed
- Anki running with AnkiConnect listening on `http://localhost:8765`

## Setup

1. **Clone and navigate to the project:**
   ```bash
   cd /home/burd/Documents/Stuff/AnkiHandler
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**

   Create or update `.env` in the project root:
   ```env
   PATH_TO_CLIPPINGS_FILE='/path/to/My Clippings.txt'
   DICTIONARY_API_URL="https://api.dictionaryapi.dev/api/v2/entries/en/"
   ```

4. **Start the API server:**
   ```bash
   uv run uvicorn api.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

## API Reference

### Create Flashcard

Creates a single flashcard in Anki.

```http
POST /create_flashcard
Content-Type: application/json

{
  "front": "Question or term",
  "back": "Answer or definition",
  "deckName": "MyDeck",      // optional, defaults to "Default"
  "modelName": "Basic",       // optional, defaults to "Basic"
  "tags": ["vocab", "french"] // optional, defaults to []
}
```

**Response:**
- `201 Created` - Returns `{"note_id": 12345}`
- `400 Bad Request` - AnkiConnect error (e.g., duplicate note)
- `502 Bad Gateway` - Cannot reach AnkiConnect

### Create Deck

Creates a new deck in Anki.

```http
POST /create_deck/{deck_name}
```

**Response:**
- `201 Created` - Returns `{"deck_id": 99}`
- `400 Bad Request` - AnkiConnect error (e.g., deck already exists)
- `502 Bad Gateway` - Cannot reach AnkiConnect

### Process Kindle Clippings

Batch-processes Kindle highlights from the configured clippings file. Automatically fetches definitions for single-word highlights and creates flashcards.

```http
POST /process_kindle_clippings
```

**Response:**
- `201 Created` - Returns summary:
  ```json
  {
    "created": 15,
    "failed": 2,
    "errors": ["duplicate note", "invalid deck"]
  }
  ```
- `400 Bad Request` - Failed to parse clippings file
- `502 Bad Gateway` - AnkiConnect unavailable during processing

## Development

### Running Tests

```bash
uv run pytest
```

Run with coverage:
```bash
uv run pytest --cov=api --cov=services --cov=models
```

### Code Architecture

**Domain Layer (`models/`)**
- `Note`: Flashcard model with front/back, deck, model name, and tags
- `Deck`: Deck metadata

**Service Layer (`services/`)**
- `kindle.py`: Parses Kindle clippings file, returns `list[Note]`
- `definition_api.py`: Fetches word definitions, returns `str | None`

**API Layer (`api/`)**
- `anki_connect.py`: HTTP client for AnkiConnect, returns domain types (int IDs) and raises custom exceptions
- `exceptions.py`: Domain-specific exceptions (`AnkiConnectError`, `AnkiConnectUnavailableError`)
- `main.py`: FastAPI endpoints that orchestrate services and translate exceptions to HTTP responses

**Error Handling Strategy:**
- Services raise domain exceptions (`AnkiConnectError`, `AnkiConnectUnavailableError`)
- API endpoints catch these and return appropriate HTTP status codes:
  - `201 Created` - Resource created successfully
  - `400 Bad Request` - Invalid input or AnkiConnect rejected the request
  - `502 Bad Gateway` - Cannot reach AnkiConnect (Anki not running or plugin not installed)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PATH_TO_CLIPPINGS_FILE` | Absolute path to Kindle's `My Clippings.txt` | Required |
| `DICTIONARY_API_URL` | Base URL for word definition API | `https://api.dictionaryapi.dev/api/v2/entries/en/` |

## Troubleshooting

**"502 Bad Gateway" when creating cards:**
- Ensure Anki desktop is running
- Verify AnkiConnect plugin is installed (Tools → Add-ons)
- Check AnkiConnect is listening on port 8765

**"400 Bad Request" with "duplicate note":**
- The flashcard already exists in Anki with identical front/back content
- AnkiConnect prevents duplicates by default

**Kindle clippings not processing:**
- Verify `PATH_TO_CLIPPINGS_FILE` in `.env` points to the correct file
- Ensure the file follows Kindle's clippings format


