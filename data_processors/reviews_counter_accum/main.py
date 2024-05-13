
import logging
import os
from reviews_counter import ReviewsCounter
from entities.book import Book
from entities.query_message import ANY_IDENTIFIER, BOOK_IDENTIFIER, REVIEW_IDENTIFIER, QueryMessage
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, initialize_config, initialize_log, initialize_workers_environment
from utils.parser import parse_book, parse_query_msg, parse_review


def initialize():
    params = ["logging_level", "id", "input_queue",
              "output_queues", "query", "previous_workers"]

    params = list(map(lambda param: (param, False), params))

    config_params = initialize_config(params)

    initialize_workers_environment(config_params)

    initialize_log(logging, config_params["logging_level"])

    return config_params


def process_eof(queue_middleware: QueueMiddleware, counter: ReviewsCounter):
    def callback():
        for title, avg in counter.get_results():
            query_msg = QueryMessage(ANY_IDENTIFIER, f"{title}\t{avg}")
            queue_middleware.send_to_all_except(
                encode(str(query_msg)), "results_0")

        counter.clear()
    queue_middleware.send_eof(callback)


def process_book(counter: ReviewsCounter, book: Book):
    counter.add_book(book)


def process_message(counter: ReviewsCounter, queue_middleware: QueueMiddleware, more_than_n, query=None):
    def callback(ch, method, properties, body):
        msg_received = decode(body)
        if msg_received == "EOF":
            process_eof(queue_middleware, counter)
            return

        identifier, data = parse_query_msg(msg_received)

        if identifier == BOOK_IDENTIFIER:
            book = parse_book(data)
            process_book(counter, book)
            return

        elif identifier == REVIEW_IDENTIFIER:
            review = parse_review(data)
            author, title, avg = counter.add_review(review)
            if title and title not in more_than_n:
                # print("Review accepted: ", review.title," | Total reviews: ", avg)
                msg = f"{title},{author}"
                if query:
                    msg = add_query_to_message(
                        msg, query)

                query_msg = QueryMessage(
                    ANY_IDENTIFIER, msg)

                queue_middleware.send("results_0", encode(str(query_msg)))
                more_than_n[title] = True

    return callback


def main():

    config_params = initialize()
    logging.debug("Config: %s", config_params)

    min_amount_of_reviews = 500
    counter = ReviewsCounter(min_amount_of_reviews)

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    more_than_n = {}
    queue_middleware.start_consuming(
        process_message(counter, queue_middleware, more_than_n, query=config_params["query"]))


if __name__ == "__main__":
    main()
