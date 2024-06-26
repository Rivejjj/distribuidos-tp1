import logging
from data_processors.data_manager.data_manager import DataManager
from accumulator import Accumulator
from accumulator_checkpoint import AccumulatorCheckpoint
from entities.authors_msg import AuthorsMessage
from entities.book_msg import BookMessage
from entities.client_dc import ClientDCMessage
from entities.eof_msg import EOFMessage
from entities.query_message import AUTHORS, BOOK, QueryMessage
from utils.initialize import decode, encode, get_queue_names
from utils.parser import parse_query_msg


class AccumulatorManager(DataManager):
    def __init__(self, config_params):
        super().__init__(config_params)
        self.accum = Accumulator()
        self.accum_cp = AccumulatorCheckpoint(self.accum)

    def process_book(self, book_msg: BookMessage):
        book = book_msg.get_book()

        msg = AuthorsMessage(
            book.authors, *book_msg.get_headers(), self.query)

        client_id = msg.get_client_id()

        if self.accum.check_valid_author(book.authors, client_id):
            if self.messages_cp.is_processed_msg(book_msg):
                logging.info(f"Already processed")
                return msg
            else:
                return

        send_author = self.accum.add_book(book, client_id)
        self.accum_cp.save(book, client_id)
        if not send_author:
            logging.info(f"Not yet")
            return
        logging.info(
            f"Author {book.authors} has published books in 10 different decades")

        return msg

    def send_to_next_worker(self, result: AuthorsMessage):
        msg = result

        if msg.get_query():
            self.queue_middleware.send_to_result(msg)
        else:
            self.queue_middleware.send_to_pool(
                encode(msg), msg.get_author())

    def process_query_message(self, msg):
        if msg.get_identifier() == BOOK and msg.get_book():
            return self.process_book(msg)

    def delete_client(self, msg: QueryMessage):
        self.accum.clear(msg)
        self.accum_cp.delete_client(msg)
        return super().delete_client(msg)
