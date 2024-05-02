from multiprocessing import Process
from threading import Thread
import time
from common.client import Client
from utils.initialize import decode, initialize_config, initialize_log


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
        print(f"[RESULTS] Received: {msg}")
        if msg == "EOF":
            break

        number, text = msg.split(':', 1)
        filename = f"query{number}.txt"
        with open(filename, 'a') as f:
            f.write(text + '\n')

    client.stop()


def run(config_params):
    client = Client(config_params["address"], config_params["port"])
    time.sleep(40)

    thread = Thread(
        target=receive_results, args=(config_params["address"], config_params["results_port"]))
    thread.start()

    # with open('results.csv', 'w') as a:
    with open(config_params["books_path"]) as file:
        i = 0
        for line in file:
            print(line.strip())
            client.send_message(line.strip())
            if i == 1000:
                break
            i += 1
            # msg = decode(client.receive_message())
            # print(msg)
            # a.write(msg + '\n')
        print(i)
    # with open(config_params["books_reviews_path"]) as file:
    #     i = 0
    #     for line in file:

    #         print(line.strip())
    #         client.send_message(line.strip())
    #         if i == 5000:
    #             break
    #         i += 1
    client.send_message("EOF")

    thread.join()

    while True:
        continue


def main():
    config_params = initialize()
    print(config_params)
    run(config_params)


if __name__ == "__main__":
    main()
