
from configparser import ConfigParser
import logging
from multiprocessing import Process
import os
import signal
import socket
from common.data_receiver import DataReceiver
from gateway.common.data_collector import DataCollector
from messages.book import Book
from rabbitmq.queue import QueueMiddleware

from utils.initialize import get_queue_names, initialize_config, initialize_log
from common.server import Server


def initialize():
    config_params = initialize_config(
        [("logging_level", True), ("port", True),
         ("results_port", True),  ("listen_backlog", True),
         ("input_queue", False), ("query_count", False),
         ("output_queues", False),
         ])

    config_params["port"] = int(config_params["port"])
    config_params["results_port"] = int(config_params["results_port"])
    config_params["query_count"] = int(config_params["query_count"])
    config_params["listen_backlog"] = int(config_params["listen_backlog"])

    initialize_log(config_params["logging_level"])
    return config_params


def signal_handler(server, data_collector_process):
    def callback(sig, frame):
        server.stop()

        data_collector_process.terminate()

    return callback


def start_data_collector(config_params):
    data_collector = DataCollector(
        config_params["results_port"],
        config_params["listen_backlog"],
        config_params["query_count"],
        input_queue=config_params["input_queue"],
    )

    data_collector.run()


def main():
    config_params = initialize()
    print("Config: ", config_params)
    server = Server(
        config_params["port"],
        config_params["listen_backlog"],
        output_queues=get_queue_names(config_params)
    )

    data_collector_process = Process(
        target=start_data_collector, args=(config_params,))

    signal.signal(signal.SIGTERM, lambda signal,
                  frame: data_collector_process.terminate())
    data_collector_process.start()

    server.run()


if __name__ == "__main__":
    main()
