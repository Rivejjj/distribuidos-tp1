
import logging
import os
from common.book_filter import BookFilter
from common.review_filter import ReviewFilter
from rabbitmq.queue import QueueMiddleware
from utils.initialize import encode, initialize_config, initialize_log
from parser_1.csv_parser import CsvParser
from gateway.common.data_receiver import DataReceiver

def initialize():
    all_params = ["logging_level", "category",
                  "published_year_range", "title_contains", "id", "last", "input_queue", "output_queue", "exchange", "save_books"]
    env = os.environ

    params = []

    for param in all_params:
        param = param.upper()
        if param in env:
            params.append((param, True))
        else:
            params.append((param, False))

    config_params = initialize_config(params)
    logging.debug("Config: %s", config_params)
    logging.info("Config: %s", config_params)
    print(config_params)

    if config_params["PUBLISHED_YEAR_RANGE"]:
        config_params["PUBLISHED_YEAR_RANGE"] = tuple(
            map(int, config_params["PUBLISHED_YEAR_RANGE"].split("-")))

    if "LAST" in config_params:
        config_params["LAST"] = bool(config_params["LAST"])

    if "ID" in config_params:
        config_params["ID"] = int(config_params["ID"])

    initialize_log(config_params["LOGGING_LEVEL"])

    return config_params


def get_queue_names(config_params):
    return [config_params["OUTPUT_QUEUE"]]


def process_message(book_filter: BookFilter, parser: CsvParser,data_receiver: DataReceiver, review_filter: ReviewFilter, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        msg_received = body.decode()
        book = data_receiver.parse_book(msg_received)

        if book and book_filter.filter(book):
            print("Book accepted: ", book.title)
            if review_filter:
                review_filter.add_title(book.title)
            queue_middleware.send_to_all(encode(str(book)))
            return

        review = data_receiver.parse_review(msg_received)
        if review and review_filter and review_filter.filter(review):
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

    parser = CsvParser()
    data_receiver = DataReceiver()
    queue_middleware.start_consuming(
        process_message(book_filter,parser,data_receiver, review_filter, queue_middleware))


if __name__ == "__main__":
    main()
