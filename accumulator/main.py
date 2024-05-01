
import logging
import os
from common.accumulator import Accumulator
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


def process_message(accum: Accumulator,parser: CsvParser, queue_middleware: QueueMiddleware ):
    def callback(ch, method, properties, body):
        msg_received = body.decode()
        if msg_received == "EOF":
            print("EOF received")
            top = accum.get_top()
            result = ""
            for i in top:
                result += f"{i[0]}: {i[1]}\n"
            print("sending to result:", result)
            queue_middleware.send_to_all(encode(top))

        book = parser.parse_csv(msg_received)
        if len(book) == 2:
            print("Book accepted: ", book)
            accum.add_book(book)

    return callback

def main():

    config_params = initialize()
    initialize_log(config_params["LOGGING_LEVEL"])
    logging.debug("Config: %s", config_params)

    top = 10
    accum = Accumulator(top)

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), exchange=config_params["EXCHANGE"], input_queue=config_params["INPUT_QUEUE"])

    parser = CsvParser()
    queue_middleware.start_consuming(
        process_message(accum, parser, queue_middleware))


if __name__ == "__main__":
    main()