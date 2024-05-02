import logging
from multiprocessing import Process
from threading import Thread
import time
from common.client import Client
from utils.initialize import decode, initialize_config, initialize_log
import csv


def initialize():

    config_params = initialize_config(
        [("logging_level", True), ("address", True), ("port", True),  ("results_port", True), ("books_path", False), ("books_reviews_path", False)])

    config_params["port"] = int(config_params["port"])
    config_params["results_port"] = int(config_params["results_port"])
    initialize_log(config_params["logging_level"])
    return config_params


def receive_results(address, port):
    client = Client(address, port)
    while True:
        msg = decode(client.receive_message())
        # print(f"[RESULTS] Received: {msg}")

        if msg == "EOF":
            break

        splitted = msg.split(':', 1)
        if len(splitted) != 2:
            continue
        number, text = splitted
        filename = f"query/query{number}.csv"
        with open(filename, 'a') as f:
            f.write(text + '\n')

    client.stop()


def send_file(client, filename, batch_size=10, max_batches=0):
    file = open(filename, "r")
    line = file.readline()
    batch = ""

    i = 0
    while line and (max_batches == 0 or i < max_batches):
        try:
            for _ in range(batch_size):
                line = file.readline()
                batch += line
            # print(f"[CLIENT] Sending batch: {batch}")
            client.send_message(batch)
            batch = ""
        except Exception as e:
            break

        i += 1
    file.close()


def run(config_params):
    client = Client(config_params["address"], config_params["port"])

    thread = Thread(
        target=receive_results, args=(config_params["address"], config_params["results_port"]))
    thread.start()

    send_file(client, config_params["books_path"])
    send_file(client, config_params["books_reviews_path"])

    client.send_message("EOF")

    thread.join()


def main():
    config_params = initialize()
    print(config_params)
    run(config_params)


if __name__ == "__main__":
    main()
