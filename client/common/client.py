import socket
import logging
from utils.sockets import safe_receive, send_message, send_success


MAX_MESSAGE_BYTES = 16
SUCCESS_MSG = "suc"
ERROR_MSG = "err"


class Client:
    def __init__(self, address, port):
        # Creates socket
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connects to server
        _socket.connect((address, port))

        self.socket = _socket

    def stop(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def __receive_message_length(self):

        msg_length = int.from_bytes(safe_receive(self.socket,
                                                 MAX_MESSAGE_BYTES).rstrip(), "little")

        logging.info(
            f"action: receive_message_length | result: success | length: {msg_length}")

        return msg_length

    def send_message(self, msg):
        send_message(self.socket, msg)

    def receive_message(self):
        msg_length = self.__receive_message_length()

        send_success(self.socket)

        msg = safe_receive(self.socket, msg_length)
        logging.info(
            f"action: receive_message | result: success | msg: {msg}")
        return msg
