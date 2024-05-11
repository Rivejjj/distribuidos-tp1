import socket
import logging
import signal
import threading
from common.data_receiver import DataReceiver
from messages.book import Book
from messages.review import Review
from utils.initialize import decode, encode
from rabbitmq.queue import QueueMiddleware
from utils.sockets import safe_receive, send_message, send_success

MAX_MESSAGE_BYTES = 16


class Server:
    def __init__(self, port, listen_backlog, output_queues=[]):
        # Initialize server socket
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self.client_sock = None

        self.queue = QueueMiddleware(
            output_queues)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        self.run_client()

    def run_client(self):
        while True:
            try:
                logging.info(f"waiting for connection")
                client_sock = self.__accept_new_connection(self._server_socket)
                self.client_sock = client_sock
                self.handle_client_connection()
            except OSError:
                # i do this so the error propagates
                self.queue.handle_sigterm()
                break

    def __accept_new_connection(self, socket):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = socket.accept()
        logging.info(
            f'action: accept_connections | result: success | ip: {addr[0]}')
        return c

    def stop(self):
        logging.info(
            'action: receive_termination_signal | result: in_progress')

        logging.info('action: closing listening socket | result: in_progress')
        self._server_socket.close()
        logging.info('action: closing listening socket | result: success')

        self._close_client_socket()

        logging.info(
            f'action: receive_termination_signal | result: success')
        self.queue.handle_sigterm()

    def _close_client_socket(self):
        logging.info('action: closing client socket | result: in_progress')
        if self.client_sock:
            self.client_sock.close()
            self.client_sock = None
        logging.info('action: closing client socket | result: success')

    def __receive_message_length(self):
        try:
            int_bytes = safe_receive(self.client_sock,
                                     MAX_MESSAGE_BYTES)

            # print("receiving message length", int_bytes)
            msg_length = int.from_bytes(int_bytes, "little")

            # logging.info(f"action: receive_message_length | result: success | length: {msg_length}")
            send_success(self.client_sock)

            return msg_length
        except socket.error as e:
            logging.error(
                f"action: receive_message_length | result: failed | error: client disconnected")
            self.queue.handle_sigterm()
            raise e
        except Exception as e:
            logging.error(
                f"action: receive_message_length | result: failed | error: {e}")
            self.queue.handle_sigterm()
            raise e

    def handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            while True:
                msg_length = self.__receive_message_length()
                logging.info(f"msg_length: {msg_length}")
                if msg_length == 0:
                    return

                msg = decode(safe_receive(
                    self.client_sock, msg_length)).rstrip()
                for a in msg.split("\n"):
                    # print(f"msg: {a}")
                    self.__process_message(a)
                # self.__send_message(msg)

        except OSError as e:
            logging.error(
                f"action: receive_message | result: fail | error: {e}")
            self.queue.handle_sigterm()
        except Exception as e:
            logging.error(
                f"action: any | result: fail | error: {e}")
            self.queue.handle_sigterm()
        self._close_client_socket()

    def __process_message(self, msg):
        # addr = self.client_sock.getpeername()
        data_receiver = DataReceiver()

        # print(f'received message: {msg}')
        

        if msg == "EOF":
            logging.info(
                f"action: receive_message | result: success | msg: {msg}")

            self.queue.send_eof()
            return

        book = data_receiver.parse_book(msg)
        if book:
            pool = [f"query{i}" for i in range(1, 5) if i != 2]
            for name in pool:
                self.queue.send_to_pool(
                    encode(str(book)), book.title, next_pool_name=name)

            query2 = "query2"
            books = Book.expand_authors(book)
            for book in books:
                self.queue.send_to_pool(
                    encode(str(book)), book.authors, next_pool_name=query2)
            # logging.info(f'sending to comp.filter | msg: {str(book)}')
            return
        
        review = data_receiver.parse_review(msg)
        if review:
            pool = [f"query{i}" for i in range(3, 5)]

            for name in pool:
                self.queue.send_to_pool(
                    encode(str(review)), review.title, next_pool_name=name)
            # logging.info(f'sending to comp.filter | msg: {str(review)}')
            return

        # logging.info(f'invalid message: {msg}')
