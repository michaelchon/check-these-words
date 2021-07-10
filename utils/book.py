import inspect
import os
import sys

import regex
import wordsegment
from bs4 import BeautifulSoup
from tika import parser

from .dictionary import Dictionary

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from config import config


class Book:
    check_these_words_regex = regex.compile(
        r"^([a-zA-Z0-9-–—_()\[\]\'/, \n]+,){5,}[a-zA-Z0-9-–—_()\[\]\'/, \n]+$"
    )
    vocabulary_words_regex = regex.compile(r"^.+?(?=\s*-|\s*–|\s*—)", regex.MULTILINE)

    def __init__(self, path):
        if type(path) != str:
            raise TypeError("String should be passed.")

        wordsegment.load()
        self.path = path
        self.pages = self.get_pages()
        self.dictionary = Dictionary(
            **{
                "from_language": "en",
                "to_language": "ru",
                "ui_language": "en",
                "api_key": config["YANDEX_DICTIONARY_API_KEY"],
            }
        )

    def get_pages(self):
        content = parser.from_file(self.path, xmlContent=True)["content"]

        soup = BeautifulSoup(content, features="lxml")

        return [
            page.get_text() for page in soup.find_all("div", attrs={"class": "page"})
        ]

    def get_records(self, page):
        check_these_words = self.get_check_these_words_from_page(page)
        vocabulary_words = list(
            map(lambda word: regex.sub("[ \n]", "", word), self.get_vocabulary_words())
        )

        records = []
        for word in check_these_words:
            try:
                vocabulary_word = self.get_vocabulary_words()[
                    vocabulary_words.index(regex.sub("[ \n]", "", word))
                ]

                record = self.get_vocabulary_record(vocabulary_word)
                record["transcription"] = f"[{record['transcription']}]"

                records.append(list(record.values()))
            except ValueError:
                continue

        return records

    def get_check_these_words_from_page(self, page):
        if type(page) != int:
            raise TypeError("Integer should be passed.")

        try:
            paragraphs = self.pages[page].split("\n\n")
            for paragraph in paragraphs:
                words = self.get_check_these_words_from_paragraph(paragraph)
                if words:
                    return words

            return []
        except IndexError:
            raise IndexError("Page does not exist.")

    def get_check_these_words_from_paragraph(self, paragraph):
        if self.check_these_words_regex.fullmatch(paragraph):
            words = paragraph.split(",")
            normalized_words = [" ".join(wordsegment.segment(word)) for word in words]
            return normalized_words

        return None

    def get_vocabulary_words(self):
        return self.vocabulary_words_regex.findall(self.get_vocabulary())

    def get_vocabulary(self):
        vocabulary_pages = [page for page in self.pages if "word list" in page.lower()]

        if not vocabulary_pages:
            raise Exception("Cannot find vocabulary in the book.")

        return "\n".join(vocabulary_pages)

    def get_vocabulary_record(self, search):
        if type(search) != str:
            raise TypeError("String should be passed.")

        search = regex.sub(r" +", " ", search)

        record_string = regex.search(
            fr"^{regex.escape(search)}.+", self.get_vocabulary(), regex.MULTILINE
        ).group(0)

        transcriptions = []
        for word in search.split(" "):
            dictionary_results = self.dictionary.search(word)
            transcription = ""
            if dictionary_results:
                transcription = dictionary_results[0].get("transcription", "-")
            if transcription:
                transcriptions.append(transcription)

        translation = regex.split(r"[-–—]", record_string)[-1].strip()

        return {
            "word": " ".join(wordsegment.segment(search)),
            "transcription": " ".join(transcriptions),
            "translation": translation,
        }
