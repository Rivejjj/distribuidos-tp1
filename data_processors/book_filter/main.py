
import logging
from entities.book import Book
from entities.query_message import BOOK_IDENTIFIER, REVIEW_IDENTIFIER, QueryMessage
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, init, initialize_config, initialize_log, initialize_workers_environment
from book_filter import BookFilter
from review_filter import ReviewFilter
from utils.parser import parse_book, parse_query_msg, parse_review


def initialize():
    all_params = ["category",
                  "published_year_range", "title_contains", "save_books", "is_equal"]

    params = list(map(lambda param: (param, False), all_params))

    filter_config_params = initialize_config(params)

    if filter_config_params["published_year_range"]:
        filter_config_params["published_year_range"] = tuple(
            map(int, filter_config_params["published_year_range"].split("-")))

    if filter_config_params["save_books"]:
        filter_config_params["save_books"] = True

    config_params = init(logging)

    config_params.update(filter_config_params)
    return config_params


def process_eof(queue_middleware: QueueMiddleware, review_filter: ReviewFilter, query=None):
    def callback():
        if review_filter:
            review_filter.clear()

    queue_middleware.send_eof(callback)


def format_for_results(book: Book, query):
    return add_query_to_message(f"{book.title},{book.authors},{book.publisher}", query)


def process_book(book_filter: BookFilter, review_filter: ReviewFilter, queue_middleware: QueueMiddleware, book: Book, query=None):
    if not book_filter.filter(book):
        return
    message = str(book)
    if query:
        message = format_for_results(book, query)
    if review_filter:
        review_filter.add_title(book.title)

    xd = len(message.split('\t'))
    logging.info(f"Sent book: {xd}")

    query_message = QueryMessage(BOOK_IDENTIFIER, message)
    queue_middleware.send_to_pool(encode(str(query_message)), book.title)


def process_review(review_filter: ReviewFilter, queue_middleware: QueueMiddleware, review):
    if not review_filter or (review_filter and not review_filter.filter(review)):
        return
    print("Review accepted: ", review.title)
    query_message = QueryMessage(REVIEW_IDENTIFIER, review)

    queue_middleware.send_to_pool(encode(str(query_message)), review.title)


def process_message(book_filter: BookFilter, review_filter: ReviewFilter, queue_middleware: QueueMiddleware, query=None):
    def callback(ch, method, properties, body):

        logging.info(f"Received new message {decode(body)}")
        msg_received = decode(body)

        if msg_received == "EOF":
            logging.info("Received EOF")
            process_eof(queue_middleware, review_filter, query)
            return

        identifier, data = parse_query_msg(msg_received)

        logging.info(f"Received message: {identifier} {data}")
        if identifier == BOOK_IDENTIFIER:
            book = parse_book(data)
            if not book:
                return
            process_book(book_filter, review_filter, queue_middleware,
                         book, query)
        elif identifier == REVIEW_IDENTIFIER:
            process_review(review_filter, queue_middleware, parse_review(data))

    return callback


def main():

    config_params = initialize()

    book_filter = BookFilter(
        category=config_params["category"],
        published_year_range=config_params["published_year_range"],
        title_contains=config_params["title_contains"],
        is_equal=config_params["is_equal"]
    )

    review_filter = None

    if config_params["save_books"]:
        review_filter = ReviewFilter()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    queue_middleware.start_consuming(
        process_message(book_filter, review_filter, queue_middleware, config_params["query"]))


if __name__ == "__main__":
    main()
