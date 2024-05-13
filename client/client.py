import socket
import logging
from utils.initialize import decode
from utils.sockets import receive, safe_receive, send_message, send_success

MAX_MESSAGE_BYTES = 16
SUCCESS_MSG = "suc"
ERROR_MSG = "err"


class Client:
    def __init__(self, address, port):
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.connect((address, port))
        self.socket = _socket

    def stop(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def send_message(self, msg):
        send_message(self.socket, msg)

    def receive_message(self):
        msg = decode(receive(self.socket)).rstrip()
        return msg
