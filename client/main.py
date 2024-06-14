import logging
from multiprocessing import Process
from client import Client
from entities.query_message import BOOK, QUERY_MSG_SEPARATOR, REVIEW
from utils.initialize import initialize_config, initialize_log
import time

def initialize():

    config_params = initialize_config(
        [("logging_level", True), ("address", True), ("port", True),  ("results_port", True), ("books_path", False), ("books_reviews_path", False)])

    config_params["port"] = int(config_params["port"])
    config_params["results_port"] = int(config_params["results_port"])
    initialize_log(logging, config_params["logging_level"])
    return config_params


def receive_results(address, port):
    client = Client(address, port)
    while True:
        msg = client.receive_message()
        # logging.info("message received: ", msg)
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


def send_file(client, filename, identifier, batch_size=10, max_batches=0):
    time.sleep(2)
    file = open(filename, "r")
    line = file.readline()
    batch = f"{identifier}{QUERY_MSG_SEPARATOR}"

    i = 0
    while line and (max_batches == 0 or i < max_batches):
        try:
            for _ in range(batch_size):
                line = file.readline()
                batch += line
            client.send_message(batch)
            batch = f"{identifier}{QUERY_MSG_SEPARATOR}"
            logging.warning(f"[CLIENT] Sent batch {batch}")
        except EOFError as e:
            print(f"[CLIENT] Finished sending file: {e}")
            break
        except OSError as e:
            print(f"[CLIENT] OSError sending file: {e}")
            break

        i += 1
    file.close()


def run(config_params):
    process = Process(target=receive_results, args=(
        config_params["address"], config_params["results_port"]))

    process.start()

    client = Client(config_params["address"], config_params["port"])

    logging.info("Sending books")
    send_file(client, config_params["books_path"], BOOK, 2)
    logging.info("Sending reviews")
    send_file(
        client, config_params["books_reviews_path"], REVIEW, 2)
    logging.info("Sending EOF")
    client.send_message("EOF")

    client.stop()
    process.join()


def main():
    config_params = initialize()
    print(config_params)
    run(config_params)


if __name__ == "__main__":
    main()
