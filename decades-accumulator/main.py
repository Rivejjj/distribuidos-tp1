
from configparser import ConfigParser
import logging
import os
from common.accumulator import Accumulator
from messages.book import Book
from rabbitmq.queue import QueueMiddleware
from utils.initialize import encode, initialize_config, initialize_log
from parser_1.csv_parser import CsvParser


def initialize():
    all_params = ["logging_level", "category",
                  "published_year_range", "title_contains", "id", "last", "input_queue", "output_queue", "exchange"]
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


def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

def get_queue_names(config_params):
    return [config_params["OUTPUT_QUEUE"]]

def process_message(accum: Accumulator, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        msg_received = body.decode()
        line = CsvParser().parse_csv(msg_received)

        book = Book(*line)
        if msg_received == "EOF":
            logging.info("Received EOF, shutting down")
            authors = accum.get_result()
            final_result = "\n".join([f"{author}" for author in authors])
            queue_middleware.send_to_all(encode(final_result))
            queue_middleware.stop_consuming()
            return

        if book and msg_received != "EOF":
            accum.add_book(book)
    return callback



def main():

    config_params = initialize()
    initialize_log(config_params["LOGGING_LEVEL"])

    logging.debug("Config: %s", config_params)

    accum = Accumulator()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), exchange=config_params["EXCHANGE"])
    
    queue_middleware.start_consuming(
        process_message(accum, queue_middleware))

if __name__ == "__main__":
    main()
