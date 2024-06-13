import logging
from book_filter import BookFilter
from data_checkpoints.messages_checkpoint import MessagesCheckpoint
from review_filter_checkpoint import ReviewFilterCheckpoint
from entities.book_msg import BookMessage
from entities.review_msg import ReviewMessage
from review_filter import ReviewFilter
from entities.query_message import BOOK, REVIEW
from rabbitmq.queue import QueueMiddleware
from utils.initialize import decode, encode, get_queue_names
from utils.parser import parse_query_msg


class FilterManager:
    def __init__(self, config_params):
        self.book_filter = BookFilter(
            category=config_params["category"],
            published_year_range=config_params["published_year_range"],
            title_contains=config_params["title_contains"],
            is_equal=config_params["is_equal"]
        )

        self.review_filter = None
        self.review_filter_cp = None

        self.messages_cp = MessagesCheckpoint('.checkpoints/msgs')

        if config_params["save_books"]:
            self.review_filter = ReviewFilter()
            self.review_filter_cp = ReviewFilterCheckpoint(
                self.review_filter,
                '.checkpoints/review_filter')

        if 'no-queue' not in config_params:
            self.queue_middleware = QueueMiddleware(get_queue_names(
                config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

        self.query = config_params["query"]

    def run(self):
        self.queue_middleware.start_consuming(
            self.process_message())

    def process_eof(self):
        def callback():
            if self.review_filter:
                self.review_filter.clear()

        self.queue_middleware.send_eof(callback)

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

    def process_message(self):
        def callback(ch, method, properties, body):

            # logging.info(f"Received new message {decode(body)}")
            msg_received = decode(body)

            if msg_received == "EOF":
                logging.info("Received EOF")
                self.process_eof()
                return

            msg = parse_query_msg(msg_received)

            if self.messages_cp.is_sent_msg(msg.get_id()):
                ch.basic_ack(method.delivery_tag)
                return

            logging.info(
                f"Received message: {msg.get_identifier()}")

            result = None
            if msg.get_identifier() == BOOK:
                if not msg.get_book():
                    ch.basic_ack(method.delivery_tag)
                    return
                result = self.process_book(msg)
            elif msg.get_identifier() == REVIEW:
                result = self.process_review(msg)

            if result is None:
                ch.basic_ack(method.delivery_tag)
                return

            msg, title = result

            self.messages_cp.save(msg.get_id())

            self.queue_middleware.send_to_pool(
                encode(msg), title)

            self.messages_cp.mark_msg_as_sent(msg.get_id())

            ch.basic_ack(method.delivery_tag)

        return callback
