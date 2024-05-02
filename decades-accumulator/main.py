
from configparser import ConfigParser
import logging
import os
from common.accumulator import Accumulator
from messages.book import Book
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, initialize_config, initialize_log, initialize_workers_environment
from parser_1.csv_parser import CsvParser


def initialize():
    all_params = ["logging_level",
                  "input_queue", "output_queues", "query", "id", "previous_workers"]

    params = list(map(lambda param: (param, False), all_params))

    config_params = initialize_config(params)
    logging.debug("Config: %s", config_params)
    logging.info("Config: %s", config_params)
    print(config_params)

    initialize_workers_environment(config_params)

    initialize_log(config_params["logging_level"])

    return config_params


def process_eof(queue_middleware: QueueMiddleware, accum: Accumulator, query=None):
    def callback():
        authors = accum.get_result()

        response = []

        for author in authors:
            msg = f"{author}"

            response.append(msg)

        final_result = "\n".join(response)

        if query:
            final_result = add_query_to_message(final_result, query)

        queue_middleware.send_to_all(encode(final_result))

        accum.clear()

    queue_middleware.send_eof(callback)



def process_message(accum: Accumulator, queue_middleware: QueueMiddleware, query=None):
    def callback(ch, method, properties, body):
        msg_received = decode(body)

        if msg_received == "EOF":
            process_eof(queue_middleware, accum, query)
            return

        book = Book.from_csv_line(msg_received)

        if book:
            accum.add_book(book)
    return callback


def main():

    config_params = initialize()

    logging.debug("Config: %s", config_params)

    accum = Accumulator()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    queue_middleware.start_consuming(
        process_message(accum, queue_middleware))


if __name__ == "__main__":
    main()
