import requests


class Dictionary:
    BASE_URL = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"

    def __init__(self, from_language, to_language, ui_language, api_key):
        self.from_language = from_language
        self.to_language = to_language
        self.ui_language = ui_language
        self.api_key = api_key

    def search(self, text):
        if type(text) != str:
            raise TypeError("String should be passed.")

        response = self.request(text)

        definitions = response.get("def", [])
        results = [
            Dictionary.generate_definition(definition) for definition in definitions
        ]

        return results

    def request(self, text):
        if type(text) != str:
            raise TypeError("String should be passed.")

        response = requests.get(
            self.BASE_URL,
            {
                "key": self.api_key,
                "ui": self.ui_language,
                "lang": f"{self.from_language}-{self.to_language}",
                "text": text,
            },
        )

        if response.status_code == 401:
            raise ValueError("API key is invalid.")
        elif response.status_code == 402:
            raise ValueError("API key is blocked.")
        elif response.status_code == 403:
            raise ValueError("Daily requests limit is exceeded.")
        elif response.status_code == 413:
            raise ValueError("Text is too long.")
        elif response.status_code == 501:
            raise ValueError("Language is not supported.")

        return response.json()

    @staticmethod
    def generate_definition(definition):
        if type(definition) != dict:
            raise TypeError("Dict should be passed.")

        return {
            "text": definition.get("text"),
            "transcription": definition.get("ts"),
            "part_of_speech": definition.get("pos"),
            "translations": Dictionary.generate_translations(definition.get("tr", [])),
        }

    @staticmethod
    def generate_translations(translations):
        if type(translations) != list:
            raise TypeError("List should be passed.")

        return [
            Dictionary.generate_translation(translation) for translation in translations
        ]

    @staticmethod
    def generate_translation(translation):
        if type(translation) != dict:
            raise TypeError("Dict should be passed.")

        return translation.get("text")
