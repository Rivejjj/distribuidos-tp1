import logging
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

    safe_receive(sock, INFO_MSG_BYTES)

    safe_send(sock, bytes_to_send)


def send_success(sock: socket.socket):
    safe_send(sock, encode("suc"))


def __receive_message_length(sock: socket.socket):
    try:
        int_bytes = safe_receive(sock,
                                 MAX_MESSAGE_BYTES)

        # print("receiving message length", int_bytes)
        msg_length = int.from_bytes(int_bytes, "little")

        # logging.info(f"action: receive_message_length | result: success | length: {msg_length}")
        send_success(sock)

        return msg_length
    except socket.error as e:
        logging.error(
            f"action: receive_message_length | result: failed | error: client disconnected")
        raise e
    except Exception as e:
        logging.error(
            f"action: receive_message_length | result: failed | error: {e}")
        raise e
