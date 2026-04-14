from dotenv import load_dotenv
import logging
import requests
import os

load_dotenv()
DICTIONARY_API_BASE_URL = os.getenv("DICTIONARY_API_URL")

_REQUEST_TIMEOUT_SECONDS = 5

logger = logging.getLogger(__name__)


def get_word_definition(word: str) -> str | None:
    if not word:
        return None
    try:
        response = requests.get(DICTIONARY_API_BASE_URL + word, timeout=_REQUEST_TIMEOUT_SECONDS)
        if response.status_code != 200:
            return None
        results = response.json()[0]
        return results["meanings"][0]["definitions"][0]["definition"]
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as e:
        logger.warning("definition lookup failed for %r: %s", word, e)
        return None
