import logging
from book_filter import BookFilter
from data_checkpoints.messages_checkpoint import MessagesCheckpoint
from data_processors.data_manager.data_manager import DataManager
from data_processors.decades_accumulator.accumulator import Accumulator
from data_processors.decades_accumulator.accumulator_checkpoint import AccumulatorCheckpoint
from entities.authors_msg import AuthorsMessage
from entities.book_msg import BookMessage
from entities.query_message import AUTHORS, BOOK
from rabbitmq.queue import QueueMiddleware
from utils.initialize import decode, encode, get_queue_names
from utils.parser import parse_query_msg


class AccumulatorManager(DataManager):
    def __init__(self, config_params):
        super().__init__(config_params)
        self.accum = Accumulator()
        self.accum_cp = AccumulatorCheckpoint(self.accum)

    def run(self):
        self.queue_middleware.start_consuming(
            self.process_message())

    def process_eof(self):
        def callback():
            return self.accum.clear()

        self.queue_middleware.send_eof(callback)

    def process_book(self, book_msg: BookMessage):
        book = book_msg.get_book()

        msg = AuthorsMessage(
            book.authors, AUTHORS, book_msg.get_id(), book_msg.get_client_id(), self.query)

        if self.messages_cp.is_processed_msg(book_msg.get_id()) and self.accum.check_valid_author(book.authors):
            return msg

        if not self.accum.add_book(book):
            return
        logging.info(
            f"Author {book.authors} has published books in 10 different decades")

        return msg

    def process_query_message(self, msg):
        if msg.get_identifier() == BOOK and msg.get_book():
            return self.process_book(msg)
