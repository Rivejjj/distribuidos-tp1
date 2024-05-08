
import logging
from common.accumulator import Accumulator
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, initialize_config, initialize_log, initialize_workers_environment
from parser_1.csv_parser import CsvParser


def initialize():
    all_params = ["logging_level", "id",
                  "input_queue", "output_queues", "query", "previous_workers"]

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
        logging.info("EOF received")
        top = accum.get_top()
        result = ""
        for i in top:
            result += f"{i[0]},{i[1]}\n"
        logging.info("sending to result:", result)
        queue_middleware.send_to_all(
            encode(add_query_to_message(result, query)))
        accum.clear()

    queue_middleware.send_eof(callback)


def process_message(accum: Accumulator, parser: CsvParser, queue_middleware: QueueMiddleware, query):
    def callback(ch, method, properties, body):
        msg_received = decode(body)
        if msg_received == "EOF":
            process_eof(queue_middleware, accum, query)
            return

        book = parser.parse_csv(msg_received)
        if len(book) == 2:
            # print("Book accepted: ", book)
            accum.add_book(book)

    return callback


def main():

    config_params = initialize()
    logging.debug("Config: %s", config_params)

    top = 10
    accum = Accumulator(top)

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    parser = CsvParser()
    queue_middleware.start_consuming(
        process_message(accum, parser, queue_middleware, config_params["query"]))


if __name__ == "__main__":
    main()
