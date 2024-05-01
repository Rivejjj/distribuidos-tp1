import socket

from utils.initialize import decode, encode

MAX_MESSAGE_BYTES = 16
INFO_MSG_BYTES = 3


def safe_send(sock: socket.socket, bytes_to_send: bytes):
    total_sent = 0

    while total_sent < len(bytes_to_send):
        n = sock.send(bytes_to_send[total_sent:])
        total_sent += n
    return


def safe_receive(sock: socket.socket, buffer_length: int):
    n = 0

    buffer = bytes()
    while n < buffer_length:
        message = sock.recv(buffer_length)
        buffer += message
        n += len(message)

    return buffer


def send_message(sock: socket.socket, msg: str):
    bytes_to_send = encode(msg)

    safe_send(sock, len(bytes_to_send).to_bytes(
        MAX_MESSAGE_BYTES, "little"))

    safe_send(sock, bytes_to_send)
