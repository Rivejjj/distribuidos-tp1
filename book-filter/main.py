
from configparser import ConfigParser
import logging
import os
from common.book_filter import BookFilter
from messages.book import Book
from rabbitmq.queue import QueueMiddleware
from utils.initialize import initialize_config, initialize_log, initialize_multi_value_environment, initialize_workers_environment


def initialize():
    params = ["logging_level", "category",
              "published_year_range", "title_contains", "id", "n", "input_queue", "output_queues"]

    config_params = initialize_config(
        map(lambda param: (param, False), params))

    if config_params["published_year_range"]:
        config_params["published_year_range"] = tuple(
            map(int, config_params["published_year_range"].split("-")))

    initialize_multi_value_environment(config_params, ["output_queues"])

    initialize_workers_environment(config_params)

    initialize_log(config_params["logging_level"])

    return config_params


def get_queue_names(config_params):
    queue_names = [(config_params["input_queue"], False)]

    for queue in config_params["output_queues"]:
        queue_names.append((queue, True))

    return queue_names


def process_message(book_filter: BookFilter, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        logging.info("Received message %s", body)
        # book = Book.from_json(body)
        # logging.info("Received book %s", book)
        # if book_filter.filter(book):
        #     logging.info("Book accepted")
        #     queue_middleware.send(output_queue, book)
        # else:
        #     logging.info("Book rejected")
    return callback


def process_eof():
    def callback(ch, method, properties, body):
        logging.info("Received EOF")
    return callback


def main():

    config_params = initialize()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), config_params["id"], config_params["n"])

    book_filter = BookFilter(
        category=config_params["category"],
        published_year_range=config_params["published_year_range"],
        title_contains=config_params["title_contains"]
    )

    queue_middleware.start_consuming(config_params["input_queue"], process_message(
        book_filter, queue_middleware), eof_callback=process_eof())


if __name__ == "__main__":
    main()
