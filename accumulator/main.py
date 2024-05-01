
import logging
import os
from common.accumulator import Accumulator
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, initialize_config, initialize_log, initialize_multi_value_environment, initialize_workers_environment
from parser_1.csv_parser import CsvParser
from gateway.common.data_receiver import DataReceiver


def initialize():
    all_params = ["logging_level", "id", "n",
                  "input_queue", "output_queues", "exchange", "query"]

    params = list(map(lambda param: (param, False), all_params))

    config_params = initialize_config(params)
    logging.debug("Config: %s", config_params)
    logging.info("Config: %s", config_params)
    print(config_params)

    if config_params["published_year_range"]:
        config_params["published_year_range"] = tuple(
            map(int, config_params["published_year_range"].split("-")))

    initialize_multi_value_environment(config_params, ["output_queues"])

    initialize_workers_environment(config_params)

    initialize_log(config_params["logging_level"])

    return config_params


def process_eof(queue_middleware: QueueMiddleware, accum: Accumulator, query=None):
    print("EOF received")
    top = accum.get_top()
    result = ""
    for i in top:
        result += add_query_to_message(f"{i[0]},{i[1]}\n", query)
    print("sending to result:", result)
    queue_middleware.send_to_all(encode(result))
    accum.clear()
    queue_middleware.send_eof()


def process_message(accum: Accumulator, parser: CsvParser, queue_middleware: QueueMiddleware, query):
    def callback(ch, method, properties, body):
        msg_received = decode(body)
        if msg_received == "EOF":
            process_eof(queue_middleware, accum, query)
            return

        book = parser.parse_csv(msg_received)
        if len(book) == 2:
            print("Book accepted: ", book)
            accum.add_book(book)

    return callback


def main():

    config_params = initialize()
    logging.debug("Config: %s", config_params)

    top = 10
    accum = Accumulator(top)

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), exchange=config_params["exchange"], input_queue=config_params["input_queue"])

    parser = CsvParser()
    queue_middleware.start_consuming(
        process_message(accum, parser, queue_middleware, query=config_params["query"]))


if __name__ == "__main__":
    main()
