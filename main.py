import logging

from tabulate import tabulate
from telegram import ParseMode, Update
from telegram.ext import Filters, MessageHandler, Updater

from config import config
from utils.book import Book
from utils.input_manager import InputManager

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

book = Book("book.pdf")


def return_records(update, _):
    records = book.get_records(int(update.message.text))
    update.message.reply_text(
        "```"
        + tabulate(
            records,
            headers=["Слово", "Транскрипция", "Перевод"],
            tablefmt="pretty",
            stralign="left",
            numalign="left",
        )
        + "```",
        parse_mode=ParseMode.MARKDOWN,
    )


def main():
    page_input = InputManager(
        "Введите страницу: ", "Вы должны ввести число, например 8.", int
    )
    page = page_input.input()

    book = Book("book.pdf")
    records = book.get_records(page)

    print(
        tabulate(
            records,
            headers=["Слово", "Транскрипция", "Перевод"],
            tablefmt="pretty",
            stralign="left",
            numalign="left",
        )
    )
    # updater = Updater(config['TELEGRAM_TOKEN'])
    # dispatcher = updater.dispatcher
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, return_records))
    # updater.start_polling()
    # updater.idle()


if __name__ == "__main__":
    main()
