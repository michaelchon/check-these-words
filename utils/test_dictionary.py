import unittest
from unittest.mock import patch

from ddt import data, ddt

from dictionary import Dictionary

api_response_translation = {
    "text": "привет",
    "pos": "noun",
}

dictionary_response_translation = "привет"

api_response_translations = [
    api_response_translation,
    {"text": "приветствие", "pos": "noun",},
]

dictionary_response_translations = [
    dictionary_response_translation,
    "приветствие",
]

api_response_definition = {
    "text": "hello",
    "pos": "noun",
    "ts": "həˈləʊ",
    "tr": api_response_translations,
}

dictionary_response_definition = {
    "text": "hello",
    "part_of_speech": "noun",
    "transcription": "həˈləʊ",
    "translations": dictionary_response_translations,
}

dictionary_response_empty_definition = {
    "text": None,
    "part_of_speech": None,
    "transcription": None,
    "translations": [],
}

api_response = {
    "head": {},
    "def": [api_response_definition],
}

dictionary_response = [dictionary_response_definition]


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


@ddt
class TestDictionary(unittest.TestCase):
    def setUp(self):
        self.dictionary = Dictionary("en", "ru", "en", "api_key")

    def test_init(self):
        self.assertEqual(self.dictionary.from_language, "en")
        self.assertEqual(self.dictionary.to_language, "ru")
        self.assertEqual(self.dictionary.ui_language, "en")
        self.assertEqual(self.dictionary.api_key, "api_key")

    @patch(
        "dictionary.requests.get",
        side_effect=lambda *args: MockResponse(api_response, 200),
    )
    def test_search(self, mocked_requests_get):
        results = self.dictionary.search("hello")

        self.assertListEqual(results, dictionary_response)

    def test_search_passing_not_string(self):
        with self.assertRaises(TypeError):
            self.dictionary.search(None)

    @patch(
        "dictionary.requests.get",
        side_effect=lambda *args: MockResponse(api_response, 200),
    )
    def test_request(self, mocked_requests_get):
        response = self.dictionary.request("hello")

        self.assertDictEqual(response, api_response)

    @data(401, 402, 403, 413, 501)
    def test_request_returning_error(self, error_code):
        with patch(
            "dictionary.requests.get",
            side_effect=lambda *args: MockResponse(None, error_code),
        ):
            self.assertRaises(ValueError, self.dictionary.request, "hello")

    def test_request_passing_not_string(self):
        with self.assertRaises(TypeError):
            self.dictionary.request(None)

    @data(
        [api_response_definition, dictionary_response_definition],
        [{}, dictionary_response_empty_definition],
    )
    def test_generate_definition(self, params):
        value, expected = params

        self.assertDictEqual(Dictionary.generate_definition(value), expected)

    def test_generate_definition_passing_not_dict(self):
        with self.assertRaises(TypeError):
            Dictionary.generate_definition(None)

    @data([api_response_translations, dictionary_response_translations], [[], []])
    def test_generate_translations(self, params):
        value, expected = params

        self.assertListEqual(Dictionary.generate_translations(value), expected)

    def test_generate_translations_passing_not_iterable(self):
        with self.assertRaises(TypeError):
            Dictionary.generate_translations(None)

    @data([api_response_translation, dictionary_response_translation], [{}, None])
    def test_generate_translation(self, params):
        value, expected = params

        self.assertEqual(Dictionary.generate_translation(value), expected)

    def test_generate_translation_passing_not_dict(self):
        with self.assertRaises(TypeError):
            Dictionary.generate_translation(None)


if __name__ == "__main__":
    unittest.main()
