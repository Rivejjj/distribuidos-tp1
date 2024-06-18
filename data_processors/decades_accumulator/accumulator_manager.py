import logging
from data_processors.data_manager.data_manager import DataManager
from accumulator import Accumulator
from accumulator_checkpoint import AccumulatorCheckpoint
from entities.authors_msg import AuthorsMessage
from entities.book_msg import BookMessage
from entities.query_message import AUTHORS, BOOK
from utils.initialize import decode, encode, get_queue_names
from utils.parser import parse_query_msg


class AccumulatorManager(DataManager):
    def __init__(self, config_params):
        super().__init__(config_params)
        self.accum = Accumulator()
        self.accum_cp = AccumulatorCheckpoint(self.accum)

    def eof_cb(self, msg):
        return self.accum.clear()

    def process_book(self, book_msg: BookMessage):
        book = book_msg.get_book()

        msg = AuthorsMessage(
            book.authors, book_msg.get_id(), book_msg.get_client_id(), self.query)

        if self.messages_cp.is_processed_msg(book_msg.get_id()) and self.accum.check_valid_author(book.authors):
            logging.info(f"Already processed")
            return msg

        send_author = self.accum.add_book(book)
        self.accum_cp.save(book)
        if not send_author:
            logging.info(f"Not yet")
            return
        logging.info(
            f"Author {book.authors} has published books in 10 different decades")

        return msg

    def send_to_next_worker(self, result: AuthorsMessage):
        msg = result
        self.queue_middleware.send_to_pool(
            encode(msg), msg.get_author())

    def process_query_message(self, msg):
        if msg.get_identifier() == BOOK and msg.get_book():
            return self.process_book(msg)
