
from configparser import ConfigParser
import logging
import os
from common.book_filter import BookFilter
from messages.book import Book
from rabbitmq.queue import QueueMiddleware
from utils.initialize import initialize_config, initialize_log


def initialize():
    params = ["logging_level", "category",
              "published_year_range", "title_contains", "id", "last", "input_queue", "output_queue"]

    config_params = initialize_config(params)

    if config_params["published_year_range"]:
        config_params["published_year_range"] = tuple(
            map(int, config_params["published_year_range"].split("-")))

    if config_params["LAST"]:
        config_params["LAST"] = bool(config_params["LAST"])

    if config_params["ID"]:
        config_params["ID"] = int(config_params["ID"])

    initialize_log(config_params["logging_level"])

    return config_params


def get_queue_names(config_params):
    id = config_params["id"]
    eof_send_queue = "EOF_1" if config_params["last"] else f"EOF_{id + 1}"
    return [config_params["input_queue"], config_params["output_queue"], f"EOF_{id}", eof_send_queue]


def process_message(book_filter: BookFilter, queue_middleware: QueueMiddleware, output_queue: str):
    def callback(ch, method, properties, body):
        book = Book.from_json(body)
        logging.info("Received book %s", book)
        if book_filter.filter(book):
            logging.info("Book accepted")
            queue_middleware.send(output_queue, book)
        else:
            logging.info("Book rejected")
    return callback


def main():

    config_params = initialize()

    queue_middleware = QueueMiddleware(get_queue_names(config_params))

    book_filter = BookFilter(
        category=config_params["category"],
        published_year_range=config_params["published_year_range"],
        title_contains=config_params["title_contains"]
    )

    queue_middleware.start_consuming(config_params["input_queue"],
                                     process_message(book_filter, queue_middleware, config_params["output_queue"]))


if __name__ == "__main__":
    main()
