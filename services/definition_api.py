from dotenv import load_dotenv
from http import HTTPStatus
import requests
import os
import pprint

load_dotenv()
DICTIONARY_API_BASE_URL = os.getenv("DICTIONARY_API_URL")


def get_word_definition(word):
    try:
        request_url = DICTIONARY_API_BASE_URL + word
        response = requests.get(request_url)
        results = response.json()[0]
        pprint.pp(results)
        definition = results["meanings"][0]["definitions"][0]["definition"]
        return definition
    except Exception as e:
        print(e)
        return HTTPStatus.BAD_REQUEST
