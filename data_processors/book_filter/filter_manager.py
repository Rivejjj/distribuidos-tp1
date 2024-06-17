import logging
from book_filter import BookFilter
from data_processors.data_manager.data_manager import DataManager
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

    def eof_cb(self, eof_msg):
        if self.review_filter:
            self.review_filter.clear()

    def send_to_next_worker(self, result):
        msg, title = result
        self.queue_middleware.send_to_pool(
            encode(msg), title)

    def process_book(self, book_msg: BookMessage):
        book = book_msg.get_book()
        if not self.book_filter.filter(book):
            return
        logging.info(f"Book accepted: {book.title}")

        if self.review_filter and not self.messages_cp.is_processed_msg(book_msg.get_id()):
            self.review_filter.add_title(book.title)
            self.review_filter_cp.save(book.title)

        return BookMessage(book, BOOK, book_msg.get_id(), book_msg.get_client_id(), self.query), book.title

    def process_review(self, review_msg: ReviewMessage):
        review = review_msg.get_review()
        if not self.review_filter or (self.review_filter and not self.review_filter.filter(review)):
            return
        logging.info(f"Review accepted: {review.title}")

        return ReviewMessage(review, REVIEW, review_msg.get_id(), review_msg.get_client_id(), self.query), review.title

    def process_query_message(self, msg):
        if msg.get_identifier() == BOOK and msg.get_book():
            return self.process_book(msg)
        elif msg.get_identifier() == REVIEW:
            return self.process_review(msg)
