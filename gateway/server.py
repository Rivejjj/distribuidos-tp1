import socket
import logging
import signal
from entities.book import Book
from entities.book_msg import BookMessage
from entities.query_message import BOOK, REVIEW
from client_parser import parse_book_from_client, parse_review_from_client
from entities.review import Review
from entities.review_msg import ReviewMessage
from utils.initialize import decode, encode
from rabbitmq.queue import QueueMiddleware
from utils.parser import parse_client_msg, parse_query_msg
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

        self.cur_id = 0
        self.client_id = 0

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
        logging.info('action: closing listening socket | result: in_progress')
        self._server_socket.close()
        logging.info('action: closing listening socket | result: success')

        self._close_client_socket()

        logging.info(f'action: receive_termination_signal | result: success')

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
        logging.info(f"Received book: {book.title}")
        pool = [(f"query{i}", i) for i in range(1, 5) if i != 2]
        for (name, i) in pool:
            q_msg = self.__create_q_msg_from_book_for_query(book.copy(), i)
            self.queue.send_to_pool(
                encode(str(q_msg)), book.title, next_pool_name=name)

        query2 = "query2"
        q_msg = self.__create_q_msg_from_book_for_query(book.copy(), 2)
        self.queue.send_to_pool(
            encode(str(q_msg)), book.authors, next_pool_name=query2)
        logging.info(f'sending to workers')

    def __process_review(self, msg):
        review = parse_review_from_client(msg)

        if not review:
            return
        logging.info(f"Received review: {review.title}")
        pool = [(f"query{i}", i)for i in range(3, 5)]

        for (name, i) in pool:
            q_msg = self.__create_q_msg_from_review_for_query(review.copy(), i)
            self.queue.send_to_pool(
                encode(str(q_msg)), review.title, next_pool_name=name)
        logging.info(f'sending to workers')

    def __process_batch(self, batch):
        if batch == "EOF":
            logging.info(
                f"RECEIVED EOF, closing connection with client {self.client_sock}")

            self.queue.send_eof()
            return

        identifier, data = parse_client_msg(batch.strip())
        msgs = data.split("\n")

        for msg in msgs:
            self.__process_message(identifier, msg)

    def __process_message(self, identifier, data):
        if identifier == BOOK:
            self.__process_book(data)

        elif identifier == REVIEW:
            self.__process_review(data)
        else:
            logging.info(f'invalid message: {identifier} {data}')

    def __eliminate_unnecesary_book_fields(self, book: Book, query_num: int):
        # Eliminate unnecesary fields from books
        fields_to_eliminate_by_query = {
            '2': ['publisher', 'categories'],
            '3': ['publisher', 'categories'],
            '4': ['publisher', 'published_year', 'authors'],
        }

        for field in fields_to_eliminate_by_query.get(str(query_num), []):
            setattr(book, field, None)

    def __eliminate_unnecesary_review_fields(self, review: Review, query_num: int):
        # Eliminate unnecesary fields from reviews
        fields_to_eliminate_by_query = {
            '3': ['text'],
            '4': ['score'],
        }

        for field in fields_to_eliminate_by_query.get(str(query_num), []):
            setattr(review, field, None)

    def __create_q_msg_from_book_for_query(self, book: Book, query_num: int):
        self.__eliminate_unnecesary_book_fields(book, query_num)
        self.cur_id += 1
        return BookMessage(book, BOOK, self.cur_id, self.client_id)

    def __create_q_msg_from_review_for_query(self, review: Review, query_num: int):
        self.__eliminate_unnecesary_review_fields(review, query_num)
        self.cur_id += 1
        return ReviewMessage(review, REVIEW, self.cur_id, self.client_id)
