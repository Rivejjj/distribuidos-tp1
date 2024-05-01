
import logging
import os
from common.book_filter import BookFilter
from common.review_filter import ReviewFilter
from messages.book import Book
from messages.review import Review
from rabbitmq.queue import QueueMiddleware
from utils.initialize import encode, get_queue_names, initialize_config, initialize_log, initialize_multi_value_environment, initialize_workers_environment
from parser_1.csv_parser import CsvParser


def initialize():
    all_params = ["logging_level", "category",
                  "published_year_range", "title_contains", "id", "n", "input_queue", "output_queue", "exchange", "save_books"]

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

    initialize_log(config_params["logging_level"])

    return config_params


def received_eof(review_filter: ReviewFilter):
    def callback():
        logging.info("Processing EOF from business logic")
        if review_filter:
            logging.info("Clearing saved reviews")
            review_filter.clear()

    return callback


def process_message(book_filter: BookFilter, review_filter: ReviewFilter, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        logging.info("Received message", body.decode())
        msg_received = body.decode()

        if msg_received == "EOF":
            logging.info("EOF received")
            received_eof(review_filter)
            return

        line = CsvParser().parse_csv(msg_received)
        book = Book(*line)

        if book and book_filter.filter(book):
            print("Book accepted: ", book.title)

            if review_filter:
                review_filter.add_title(book.title)

            queue_middleware.send_to_all(encode(str(book)))

            return

        review = Review(*line)

        if review and review_filter.filter(review):
            print("Review accepted: ", review.title)
            queue_middleware.send_to_all(encode(str(review)))
    return callback


def main():

    config_params = initialize()

    book_filter = BookFilter(
        category=config_params["category"],
        published_year_range=config_params["published_year_range"],
        title_contains=config_params["title_contains"]
    )

    review_filter = None

    if config_params["save_books"]:
        review_filter = ReviewFilter()

    queue_middleware = QueueMiddleware(
        get_queue_names(config_params),
        input_queue=config_params["input_queue"],
        exchange=config_params["exchange"],
        id=config_params["id"],
        total_workers=config_params["n"],
        eof_callback=received_eof(review_filter)
    )

    queue_middleware.start_consuming(
        process_message(book_filter, review_filter, queue_middleware))


if __name__ == "__main__":
    main()
