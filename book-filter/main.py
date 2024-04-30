
import logging
import os
from common.book_filter import BookFilter
from common.review_filter import ReviewFilter
from messages.book import Book
from messages.review import Review
from rabbitmq.queue import QueueMiddleware
from utils.initialize import encode, initialize_config, initialize_log, initialize_multi_value_environment, initialize_workers_environment
from parser_1.csv_parser import CsvParser


def initialize():
    all_params = ["logging_level", "category",
                  "published_year_range", "title_contains", "id", "last", "input_queue", "output_queue", "exchange", "save_books"]

    params = list(map(lambda param: (param, False), all_params))

    config_params = initialize_config(params)
    logging.debug("Config: %s", config_params)
    logging.info("Config: %s", config_params)
    print(config_params)

    if config_params["published_year_range"]:
        config_params["published_year_range"] = tuple(
            map(int, config_params["published_year_range"].split("-")))

    initialize_multi_value_environment(config_params, ["output_queue"])

    initialize_workers_environment(config_params)

    initialize_log(config_params["LOGGING_LEVEL"])

    return config_params


def get_queue_names(config_params):
    return [config_params["OUTPUT_QUEUE"]]


def process_message(book_filter: BookFilter, review_filter: ReviewFilter, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        logging.info("Received message", body.decode())
        msg_received = body.decode()
        line = CsvParser().parse_csv(msg_received)
        book = Book(*line)

        if book and book_filter.filter(book):
            print("Book accepted: ", book.title)

            if not review_filter:
                queue_middleware.send_to_all(encode(str(book)))
            else:
                review_filter.add_title(book.title)

            return

        review = Review(*line)

        if review and review_filter.filter(review):
            print("Review accepted: ", review.title)
            queue_middleware.send_to_all(encode(str(review)))
    return callback


def main():

    config_params = initialize()

    book_filter = BookFilter(
        category=config_params["CATEGORY"],
        published_year_range=config_params["PUBLISHED_YEAR_RANGE"],
        title_contains=config_params["TITLE_CONTAINS"]
    )

    review_filter = None

    if config_params["SAVE_BOOKS"]:
        review_filter = ReviewFilter()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), exchange=config_params["EXCHANGE"], input_queue=config_params["INPUT_QUEUE"])

    queue_middleware.start_consuming(
        process_message(book_filter, review_filter, queue_middleware))


if __name__ == "__main__":
    main()
