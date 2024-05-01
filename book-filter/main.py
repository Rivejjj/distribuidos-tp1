
import logging
import os
from common.book_filter import BookFilter
from common.review_filter import ReviewFilter
from messages.book import Book
from messages.review import Review
from rabbitmq.queue import QueueMiddleware
from utils.data_receiver import DataReceiver
from utils.initialize import decode, encode, get_queue_names, initialize_config, initialize_log, initialize_multi_value_environment, initialize_workers_environment
from parser_1.csv_parser import CsvParser


def initialize():
    all_params = ["logging_level", "category",
                  "published_year_range", "title_contains", "id", "n", "input_queue", "output_queues", "exchange", "save_books"]

    params = list(map(lambda param: (param, False), all_params))

    config_params = initialize_config(params)
    logging.debug("Config: %s", config_params)
    logging.info("Config: %s", config_params)
    print(config_params)

    if config_params["published_year_range"]:
        config_params["published_year_range"] = tuple(
            map(int, config_params["published_year_range"].split("-")))

    initialize_multi_value_environment(config_params, ["output_queues"])

    initialize_workers_environment(config_params)

    initialize_log(config_params["logging_level"])

    return config_params


def process_eof(queue_middleware: QueueMiddleware, review_filter: ReviewFilter):
    if review_filter:
        review_filter.clear()

    queue_middleware.send_eof()


def process_message(book_filter: BookFilter, review_filter: ReviewFilter, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        print("Received message", body.decode())
        msg_received = decode(body)

        if msg_received == "EOF":
            process_eof(queue_middleware, review_filter)
            return

        print("Line: ", body)

        book = Book.from_csv_line(msg_received)

        if book and book_filter.filter(book):
            print("Book accepted: ", book.title)

            if not review_filter:
                queue_middleware.send_to_all(encode(str(book)))
            else:
                review_filter.add_title(book.title)

            return

        review = Review.from_csv_line(msg_received)

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

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), exchange=config_params["exchange"], input_queue=config_params["input_queue"])

    queue_middleware.start_consuming(
        process_message(book_filter, review_filter, queue_middleware))


if __name__ == "__main__":
    main()
