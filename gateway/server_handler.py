import logging
from multiprocessing import Event
import signal
import socket
from entities.book import Book
from entities.book_msg import BookMessage
from entities.eof_msg import EOFMessage
from entities.query_message import BOOK, REVIEW
from entities.review import Review
from entities.review_msg import ReviewMessage
from entities.client_dc import ClientDCMessage
from client_parser import parse_book_from_client, parse_review_from_client
from rabbitmq.queue import QueueMiddleware
from utils.initialize import decode, encode, uuid
from utils.parser import parse_client_msg
from utils.sockets import receive


TIMEOUT = 5


class ClientHandler:
    def __init__(self, client_sock: socket.socket, output_queues, client_id):
        # Initialize server socket
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())

        self.client_sock = client_sock

        self.queue = QueueMiddleware(
            output_queues)

        self.cur_id = 0
        self.client_id = client_id

    def _close_client_socket(self):
        logging.info(
            f'[{self.client_id}] action: closing client socket | result: in_progress')
        self.queue.send_to_all(encode(ClientDCMessage(uuid(), self.client_id)))
        logging.info(f"Sending client disconnect message {self.client_id}")
        if self.client_sock:
            self.client_sock.close()
            self.client_sock = None

        logging.info(
            f'[{self.client_id}] action: closing client socket | result: success')

    def handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            self.client_sock.settimeout(TIMEOUT)

            while True:
                msg = decode(receive(self.client_sock)).rstrip()
                self.__process_batch(msg)
        except socket.timeout as e:
            logging.error(f"[{self.client_id}] Socket timeout")
        except OSError as e:
            logging.error(
                f"[{self.client_id}] action: receive_message | result: fail | error: {e}")
        except Exception as e:
            logging.error(
                f"[{self.client_id}] action: any | result: fail | error: {e}")
        self._close_client_socket()

    def __process_book(self, msg):
        book = parse_book_from_client(msg)
        if not book:
            return
        logging.info(
            f"[{self.client_id}] Received book: {book.title} {self.client_id}")
        pool = [(f"query{i}", i) for i in range(1, 5) if i != 2]
        for (name, i) in pool:
            q_msg = self.__create_q_msg_from_book_for_query(book.copy(), i)
            self.queue.send_to_pool(
                encode(q_msg), book.title, next_pool_name=name)

        query2 = "query2"
        q_msg = self.__create_q_msg_from_book_for_query(book.copy(), 2)
        self.queue.send_to_pool(
            encode(q_msg), book.authors, next_pool_name=query2)
        logging.info(f'[{self.client_id}] sending to workers')

    def __process_review(self, msg):
        review = parse_review_from_client(msg)

        if not review:
            return
        logging.info(f"[{self.client_id}] Received review: {review.title}")
        pool = [(f"query{i}", i)for i in range(3, 5)]

        for (name, i) in pool:
            q_msg = self.__create_q_msg_from_review_for_query(review.copy(), i)
            self.queue.send_to_pool(
                encode(str(q_msg)), review.title, next_pool_name=name)
        logging.info(f'[{self.client_id}] sending to workers')

    def __process_batch(self, batch):
        if batch == "EOF":
            logging.info(
                f"[{self.client_id}] RECEIVED EOF, closing connection with client {self.client_sock}")

            self.cur_id += 1
            self.queue.send_eof(EOFMessage(self.cur_id, self.client_id))
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
            logging.info(
                f'[{self.client_id}] invalid message: {identifier} {data}')

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
        return BookMessage(book, self.cur_id, self.client_id)

    def __create_q_msg_from_review_for_query(self, review: Review, query_num: int):
        self.__eliminate_unnecesary_review_fields(review, query_num)
        self.cur_id += 1
        return ReviewMessage(review, self.cur_id, self.client_id)

    def stop(self):
        logging.info(
            '[{self.client_id}] action: receive_termination_signal | result: in_progress')
        self._close_client_socket()
        logging.info(
            f'[{self.client_id}] action: receive_termination_signal | result: success')


def create_client_handler(client_socket, output_queues, client_id):
    c_handler = ClientHandler(client_socket, output_queues, client_id)

    c_handler.handle_client_connection()
