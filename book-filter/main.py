
from configparser import ConfigParser
import logging
import os
from common.book_filter import BookFilter
from messages.book import Book
from rabbitmq.queue import QueueMiddleware
from utils.initialize import initialize_config, initialize_log
from parser_1.csv_parser import CsvParser

def initialize():
    all_params = ["logging_level","category",
             "published_year_range", "title_contains", "id","last", "input_queue", "output_queue"]
    env = os.environ

    params = []

    for param in all_params:
        param = param.upper()
        if param in env:
            params.append((param,True))
        else:
            params.append((param,False))
        

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
    id = config_params["ID"]
    eof_send_queue = "EOF_1" if config_params["LAST"] else f"EOF_{id + 1}"
    return [config_params["INPUT_QUEUE"], config_params["OUTPUT_QUEUE"], f"EOF_{id}", eof_send_queue]


def process_message(book_filter: BookFilter, queue_middleware: QueueMiddleware, output_queue: str, file):
    def callback(ch, method, properties, body):
        msg_received = body.decode()
        line = CsvParser().parse_csv(msg_received)
        book = Book(*line)
        
        if book and book_filter.filter(book):
            print("Book accepted: %s", book.title)
            queue_middleware.send(output_queue, str(book))
            file.write(book.title + "\n")
    return callback


def main():

    config_params = initialize()


    book_filter = BookFilter(
        category=config_params["CATEGORY"],
        published_year_range=config_params["PUBLISHED_YEAR_RANGE"],
        title_contains=config_params["TITLE_CONTAINS"]
    )
    file = open("output.txt", "w")
    queue_middleware = QueueMiddleware(get_queue_names(config_params))
    
    print("Starting to consume")
    queue_middleware.start_consuming(config_params["INPUT_QUEUE"],
                                     process_message(book_filter, queue_middleware, config_params["OUTPUT_QUEUE"], file))


if __name__ == "__main__":
    main()
