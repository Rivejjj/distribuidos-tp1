
from configparser import ConfigParser
import logging
import os
import socket
from common.data_receiver import DataReceiver
from messages.book import Book

from rabbitmq.queue import Queue
from utils.initialize import initialize_config, initialize_log
from common.server import Server


def initialize():
    config_params = initialize_config(
        [("logging_level", True), ("port", True),  ("listen_backlog", True)])

    config_params["port"] = int(config_params["port"])
    config_params["listen_backlog"] = int(config_params["listen_backlog"])

    initialize_log(config_params["logging_level"])
    return config_params


def main():
    config_params = initialize()

    server = Server(config_params["port"], config_params["listen_backlog"])
    server.run()

    # logging.info("Sending message to queue")

    # queue = Queue("query_queue")

    # logging.info("Sending message to queue")
    # queue.send('Hello world!')

    # accum.add_book(test_book)


if __name__ == "__main__":
    main()
