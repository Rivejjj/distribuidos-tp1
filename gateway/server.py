import socket
import logging
import signal
from entities.query_message import BOOK_IDENTIFIER, REVIEW_IDENTIFIER, QueryMessage
from client_parser import parse_book_from_client, parse_review_from_client
from utils.initialize import decode, encode
from rabbitmq.queue import QueueMiddleware
from utils.parser import parse_query_msg
from utils.sockets import receive


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

    def _close_client_socket(self):
        logging.info('action: closing client socket | result: in_progress')
        if self.client_sock:
            self.client_sock.close()
            self.client_sock = None
        logging.info('action: closing client socket | result: success')

    def handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            while True:
                msg = decode(receive(self.client_sock)).rstrip()
                self.__process_batch(msg)

        except OSError as e:
            logging.error(
                f"action: receive_message | result: fail | error: {e}")
        except Exception as e:
            logging.error(
                f"action: any | result: fail | error: {e}")
        self._close_client_socket()

    def __process_book(self, msg):
        book = parse_book_from_client(msg)
        if not book:
            return
        logging.info(f"Received book: {book}")
        query_message = QueryMessage(BOOK_IDENTIFIER, book)
        logging.info(f"Sending to workers {query_message}")
        pool = [f"query{i}" for i in range(1, 5) if i != 2]
        for name in pool:
            self.queue.send_to_pool(
                encode(str(query_message)), book.title, next_pool_name=name)

        query2 = "query2"
        self.queue.send_to_pool(
            encode(str(query_message)), book.authors, next_pool_name=query2)
        logging.info(f'sending to workers')

    def __process_review(self, msg):
        review = parse_review_from_client(msg)

        if not review:
            return
        logging.info(f"Received review: {review.title}")
        query_message = QueryMessage(REVIEW_IDENTIFIER, review)
        pool = [f"query{i}" for i in range(3, 5)]

        for name in pool:
            self.queue.send_to_pool(
                encode(str(query_message)), review.title, next_pool_name=name)
        logging.info(f'sending to workers')

    def __process_batch(self, batch):
        if batch == "EOF":
            logging.info(
                f"action: receive_message | result: success | msg: {batch}")

            self.queue.send_eof()
            return

        identifier, data = parse_query_msg(batch.strip())

        msgs = data.split("\n")

        for msg in msgs:
            self.__process_message(identifier, msg)

    def __process_message(self, identifier, data):
        logging.info(
            f"action: receive_message | result: success | msg: {identifier}")

        if identifier == BOOK_IDENTIFIER:
            self.__process_book(data)

        elif identifier == REVIEW_IDENTIFIER:
            self.__process_review(data)
        else:
            logging.info(f'invalid message: {identifier} {data}')
