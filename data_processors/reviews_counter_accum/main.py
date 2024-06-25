
import logging
import os
from multiprocessing import Process
from reviews_counter import ReviewsCounter
from entities.book import Book
from entities.query_message import BOOK, REVIEW, TITLE_AUTHORS, TITLE_SCORE, QueryMessage
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, init
from utils.parser import parse_book, parse_query_msg, parse_review
from monitor.monitor_client import MonitorClient

def send_heartbeat(name):
    logging.warning(f"Starting monitor client with name {name}")
    monitor_client = MonitorClient(name)
    monitor_client.run()

def process_eof(queue_middleware: QueueMiddleware, counter: ReviewsCounter):
    def callback():
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

        if identifier == BOOK:
            book = parse_book(data)
            process_book(counter, book)
            return

        elif identifier == REVIEW:
            review = parse_review(data)
            author, title, avg = counter.add_review(review)
            if title:
                query_msg = QueryMessage(TITLE_SCORE, f"{title}\t{avg}")
                queue_middleware.send_to_all_except(
                    encode(str(query_msg)), "results_0")

                if title not in more_than_n:
                    # print("Review accepted: ", review.title," | Total reviews: ", avg)
                    msg = f"{title}\t{author}"
                    if query:
                        msg = add_query_to_message(
                            msg, query)

                    query_msg = QueryMessage(
                        TITLE_AUTHORS, msg)

                    queue_middleware.send("results_0", encode(str(query_msg)))
                    more_than_n[title] = True
    return callback


def main():

    config_params = init(logging)

    logging.debug("Config: %s", config_params)

    min_amount_of_reviews = 500
    counter = ReviewsCounter(min_amount_of_reviews)

    process = Process(target=send_heartbeat, args=(config_params["name"],))
    process.start()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    more_than_n = {}
    try:
        queue_middleware.start_consuming(
            process_message(counter, queue_middleware, more_than_n, query=config_params["query"]))
    except OSError as e:
        logging.error(f"Error while consuming from queue {e}")
    except AttributeError as e :
        logging.error(f"Error while consuming from queue: {e}")

if __name__ == "__main__":
    main()
