
import logging
from accumulator import Accumulator
from entities.book import Book
from entities.query_message import AUTHORS, BOOK, QueryMessage
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, init
from utils.parser import parse_book, parse_query_msg


def process_eof(queue_middleware: QueueMiddleware, accum: Accumulator):
    def callback():
        accum.clear()

    queue_middleware.send_eof(callback)


def process_book(accum: Accumulator, queue_middleware: QueueMiddleware, book: Book, query=None):
    if accum.add_book(book):
        logging.info(
            f"Author {book.authors} has published books in 10 different decades")
        final_result = add_query_to_message(
            book.authors, query)

        query_message = QueryMessage(AUTHORS, final_result)
        queue_middleware.send_to_all(encode(str(query_message)))


def process_message(accum: Accumulator, queue_middleware: QueueMiddleware, query=None):
    def callback(ch, method, properties, body):
        msg_received = decode(body)

        if msg_received == "EOF":
            process_eof(queue_middleware, accum)
            return

        identifier, data = parse_query_msg(msg_received)

        if identifier != BOOK:
            return
        logging.info(f"Received data: {data}")
        book = parse_book(data)

        if not book:
            return
        logging.info(f"Received book: {book}")

        process_book(accum, queue_middleware, book, query)
    return callback


def main():

    config_params = init(logging)

    accum = Accumulator()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    queue_middleware.start_consuming(
        process_message(accum, queue_middleware, query=config_params["query"]))


if __name__ == "__main__":
    main()
