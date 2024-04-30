
from configparser import ConfigParser
import logging
import os
import socket
from common.data_receiver import DataReceiver
from messages.book import Book
from rabbitmq.queue import QueueMiddleware

from utils.initialize import initialize_config, initialize_log
from common.server import Server


def initialize():
    config_params = initialize_config(
        [("logging_level", True), ("port", True),  ("listen_backlog", True), ("exchange", False)])

    config_params["port"] = int(config_params["port"])
    config_params["listen_backlog"] = int(config_params["listen_backlog"])

    initialize_log(config_params["logging_level"])
    return config_params


def main():
    config_params = initialize()
    print("Config: ", config_params)
    server = Server(
        config_params["port"], config_params["listen_backlog"], exchange=config_params["exchange"])
    server.run()


if __name__ == "__main__":
    main()
