import logging
import socket

from utils.initialize import decode, encode

MAX_MESSAGE_BYTES = 16
INFO_MSG_BYTES = 3

MAX_READ_SIZE = 1024


def safe_send(sock: socket.socket, bytes_to_send: bytes):
    total_sent = 0

    while total_sent < len(bytes_to_send):
        n = sock.send(bytes_to_send[total_sent:])
        total_sent += n
    return


def safe_receive(sock: socket.socket, buffer_length: int):
    data = b''
    while len(data) < buffer_length:
        bytes_remaining = buffer_length - len(data)
        new_data = sock.recv(min(MAX_READ_SIZE, bytes_remaining))
        if not new_data:
            raise EOFError("EOF reached while reading data")
        data += new_data
    return data


def send_message(sock: socket.socket, msg: str):
    bytes_to_send = encode(msg)

    total_msg = len(bytes_to_send).to_bytes(
        MAX_MESSAGE_BYTES, "big") + bytes_to_send

    safe_send(sock, total_msg)


def send_success(sock: socket.socket):
    safe_send(sock, encode("suc"))


def receive(sock: socket.socket):
    msg_length = safe_receive(sock, MAX_MESSAGE_BYTES)
    return safe_receive(sock, int.from_bytes(msg_length, "big"))
