import logging
from book_filter import BookFilter
from data_processors.data_manager.data_manager import DataManager
from entities.eof_msg import EOFMessage
from review_filter_checkpoint import ReviewFilterCheckpoint
from entities.book_msg import BookMessage
from entities.review_msg import ReviewMessage
from review_filter import ReviewFilter
from entities.query_message import BOOK, REVIEW
from utils.initialize import encode


class FilterManager(DataManager):
    def __init__(self, config_params):
        super().__init__(config_params)

        self.book_filter = BookFilter(
            category=config_params["category"],
            published_year_range=config_params["published_year_range"],
            title_contains=config_params["title_contains"],
            is_equal=config_params["is_equal"]
        )

        self.review_filter = None
        self.review_filter_cp = None

        if config_params["save_books"]:
            self.review_filter = ReviewFilter()
            self.review_filter_cp = ReviewFilterCheckpoint(
                self.review_filter,
                '.checkpoints/review_filter')

    def eof_cb(self, eof_msg: EOFMessage):
        if self.review_filter:
            self.review_filter.clear(eof_msg)

    def send_to_next_worker(self, result):
        msg, title = result
        logging.info(f"Send to next queue: {msg} {title}")
        self.queue_middleware.send_to_pool(
            encode(msg), title)

    def process_book(self, book_msg: BookMessage):
        logging.info(f"New book")
        book = book_msg.get_book()
        if not self.book_filter.filter(book):
            return
        logging.info(f"Book accepted: {book.title}")

        if self.review_filter and not self.messages_cp.is_processed_msg(book_msg):
            self.review_filter.add_title(book.title, book_msg.get_client_id())
            self.review_filter_cp.save(book.title)

        return BookMessage(book, *book_msg.get_headers()), book.title

    def process_review(self, review_msg: ReviewMessage):
        review = review_msg.get_review()
        if not self.review_filter or (self.review_filter and not self.review_filter.filter(review, review_msg.get_client_id())):
            return
        logging.info(f"Review accepted: {review.title}")

        return ReviewMessage(review, *review_msg.get_headers()), review.title

    def process_query_message(self, msg):
        if msg.get_identifier() == BOOK and msg.get_book():
            return self.process_book(msg)
        elif msg.get_identifier() == REVIEW:
            return self.process_review(msg)

        logging.info(f"Not detected {msg.get_book()}")
