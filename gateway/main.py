import logging
from common.data_receiver import DataReceiver
from messages.book import Book

from rabbitmq.queue import QueueMiddleware
from utils.initialize import get_queue_names, initialize_config, initialize_log, initialize_multi_value_environment, encode
from common.server import Server


def initialize():
    config_params = initialize_config(
        [("logging_level", True), ("port", True),  ("listen_backlog", True), ("output_queues", False), ("input_queue", False)])

    config_params["port"] = int(config_params["port"])
    config_params["listen_backlog"] = int(config_params["listen_backlog"])

    initialize_multi_value_environment(config_params, ["output_queues"])

    initialize_log(config_params["logging_level"])
    return config_params


def main():
    config_params = initialize()

    queue = QueueMiddleware(get_queue_names(config_params))

    logging.info("Sending message to queue")
    queue.send_to_all(encode("EOF"))

    # server = Server(config_params["port"], config_params["listen_backlog"])
    # server.run()

    # logging.info("Sending message to queue")


if __name__ == "__main__":
    main()
