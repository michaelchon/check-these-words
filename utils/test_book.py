import unittest
from unittest.mock import patch

from book import Book

mock_paragraph = (
    "gifted, composer, preserve, follow in sb's footsteps, forefather, worthy"
)
mock_vocabulary_words = [
    "gifted",
    "composer",
]
mock_pages = [
    "introduction",
    "page1",
    f"block1\n\n{mock_paragraph}\n\nblock3",
    "page3",
    "word list introduction",
    f"word list\n{mock_vocabulary_words[0]} - [translation] - (pos) - перевод\n{mock_vocabulary_words[1]} - [translation] - (pos) - перевод",
]
mock_normalized_words = [
    "gifted",
    "composer",
    "preserve",
    "follow in sb's footsteps",
    "forefather",
    "worthy",
]


class MockPage:
    def __init__(self, text):
        self.text = text

    def get_text(self):
        return self.text


class MockSoup:
    def find_all(self, *args, **kwargs):
        return [MockPage(page) for page in mock_pages]


class MockDictionary:
    def __init__(self):
        self.name = "mock"

    def search(self):
        return [{"transcription": "ts"}]


class TestBook(unittest.TestCase):
    @patch("book.wordsegment")
    @patch("book.parser.from_file")
    @patch("book.BeautifulSoup", return_value=MockSoup)
    def setUp(self, mocked_word_segment, mocked_from_file, mocked_bs):
        self.book = Book("book.pdf")

    def test_init(self):
        self.assertEqual(self.book.path, "book.pdf")

    def test_init_passing_not_string(self):
        with self.assertRaises(TypeError):
            Book(None)

    @patch("book.parser.from_file")
    @patch("book.BeautifulSoup", return_value=MockSoup)
    def test_get_pages(self, mocked_from_file, mocked_bs):
        pages = self.book.get_pages()

        self.assertListEqual(pages, mock_pages)

    @patch("book.wordsegment.segment", side_effect=lambda word: word.strip().split(" "))
    def test_get_check_these_words_from_page(self, mocked_segment):
        words = self.book.get_check_these_words_from_page(2)

        self.assertListEqual(words, mock_normalized_words)

    def test_get_check_these_words_from_page_passing_invalid_number(self):
        with self.assertRaises(IndexError):
            self.book.get_check_these_words_from_page(2000)

    def test_get_check_these_words_from_page_passing_not_int(self):
        with self.assertRaises(TypeError):
            self.book.get_check_these_words_from_page(None)

    @patch("book.wordsegment.segment", side_effect=lambda word: word.strip().split(" "))
    def test_get_check_these_words_from_paragraph(self, mocked_segment):
        words = self.book.get_check_these_words_from_paragraph(mock_paragraph)

        self.assertListEqual(words, mock_normalized_words)

    def test_get_check_these_words_from_empty_paragraph(self):
        self.assertEqual(self.book.get_check_these_words_from_paragraph(""), None)

    def test_get_check_these_words_from_paragraph_passing_not_string(self):
        with self.assertRaises(TypeError):
            self.book.get_check_these_words_from_paragraph(None)

    def test_get_vocabulary_words(self):
        vocabulary_words = self.book.get_vocabulary_words()

        self.assertListEqual(vocabulary_words, mock_vocabulary_words)

    def test_get_vocabulary(self):
        vocabulary = self.book.get_vocabulary()

        self.assertEqual(
            vocabulary,
            "\n".join([page for page in mock_pages if "word list" in page.lower()]),
        )

    @patch(
        "book.Dictionary.search", side_effect=lambda *args: [{"transcription": "ts"}]
    )
    def test_get_vocabulary_record(self, mocked_dictionary):
        record = self.book.get_vocabulary_record("gifted")

        self.assertDictEqual(
            record, {"word": "gifted", "transcription": "ts", "translation": "перевод"}
        )

    def test_get_vocabulary_record_passing_not_string(self):
        with self.assertRaises(TypeError):
            self.book.get_vocabulary_record(None)


if __name__ == "__main__":
    unittest.main()
