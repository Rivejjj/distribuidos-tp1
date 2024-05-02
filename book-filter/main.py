
import logging
from common.book_filter import BookFilter
from common.review_filter import ReviewFilter
from messages.book import Book
from messages.review import Review
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, initialize_config, initialize_log, initialize_workers_environment


def initialize():
    all_params = ["logging_level", "category",
                  "published_year_range", "title_contains", "id", "input_queue", "output_queues", "save_books", "query", "previous_workers"]

    params = list(map(lambda param: (param, False), all_params))

    config_params = initialize_config(params)
    logging.debug("Config: %s", config_params)
    logging.info("Config: %s", config_params)
    print(config_params)

    if config_params["published_year_range"]:
        config_params["published_year_range"] = tuple(
            map(int, config_params["published_year_range"].split("-")))

    initialize_workers_environment(config_params)

    initialize_log(config_params["logging_level"])

    return config_params


def process_eof(queue_middleware: QueueMiddleware, review_filter: ReviewFilter, query=None):
    def callback():
        if review_filter:
            review_filter.clear()

    queue_middleware.send_eof(callback)


def format_for_results(book: Book, query):
    return add_query_to_message(f"{book.title},{book.authors},{book.publisher}", query)


def process_message(book_filter: BookFilter, review_filter: ReviewFilter, queue_middleware: QueueMiddleware, query=None):
    def callback(ch, method, properties, body):

        #print("Received message", body.decode())
        msg_received = decode(body)

        if msg_received == "EOF":
            process_eof(queue_middleware, review_filter, query)
            return

        # logging.info("Line: ", body)

        book = Book.from_csv_line(msg_received)

        if book and book_filter.filter(book):
            print("Book accepted: ", book.title)
            message = str(book)
            if not review_filter:
                if query:
                    message = format_for_results(book, query)
                queue_middleware.send_to_pool(encode(message), book.title)

            else:
                review_filter.add_title(book.title)
                queue_middleware.send_to_all(encode(message))
            return

        review = Review.from_csv_line(msg_received)
        if review and review_filter and review_filter.filter(review):
            message = str(review)

            print("Review accepted: ", review.title)
            queue_middleware.send_to_pool(encode(message), review.title)
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
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    queue_middleware.start_consuming(
        process_message(book_filter, review_filter, queue_middleware, config_params["query"]))


if __name__ == "__main__":
    main()
