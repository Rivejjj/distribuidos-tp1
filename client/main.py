
import logging
import socket
from utils.initialize import initialize_config, initialize_log
import time


def initialize():

    config_params = initialize_config(
        [("logging_level", True), ("address", True), ("port", True), ("books_path", False), ("books_reviews_path", False)])

    config_params["port"] = int(config_params["port"])
    initialize_log(config_params["logging_level"])
    return config_params


def send_message(socket, message: str):
    if message == "EOF":
        print("EOF sent")
    socket.send(message.encode())


def create_connection(address: str, port: int):
    # Creates socket
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connects to server
    _socket.connect((address, port))
    return _socket


def close_connection(socket):
    socket.close()


def main():
    config_params = initialize()
    print(config_params)
    socket = create_connection(config_params["address"], config_params["port"])
    with open(config_params["books_path"]) as file:
        i = 0
        for line in file:
            send_message(socket, line)
            if i == 1000:
                break
            i += 1
    # with open(config_params["books_reviews_path"]) as file:
    with open("/data/ratings_reduced.csv") as file:
        i = 0
        for line in file:
            send_message(socket, line)
            # if i > 1000:
            #     break
            # i += 1

    print(i)
    send_message(socket, "EOF")
    socket.recv(1024)
    close_connection(socket)


if __name__ == "__main__":
    main()
