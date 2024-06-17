from data_processors.data_manager.data_manager import DataManager
from book_authors_cp import BookAuthorsCheckpoint
from reviews_counter_cp import ReviewsCounterCheckpoint
from reviews_counter import ReviewsCounter
from entities.book_msg import BookMessage
from entities.query_message import BOOK, REVIEW, TITLE_AUTHORS, TITLE_SCORE
from entities.review_msg import ReviewMessage
from entities.title_authors_msg import TitleAuthorsMessage
from entities.title_score_msg import TitleScoreMessage
from utils.initialize import encode


class ReviewsCounterManager(DataManager):
    def __init__(self, config_params):
        super().__init__(config_params)
        self.counter = ReviewsCounter()
        self.reviews_counter_cp = ReviewsCounterCheckpoint(self.counter)
        self.book_authors_cp = BookAuthorsCheckpoint(self.counter)
        self.sent_titles = set()

    def run(self):
        self.queue_middleware.start_consuming(
            self.process_message())

    def eof_cb(self, msg):
        return self.counter.clear()

    def process_book(self, book_msg: BookMessage):
        if self.messages_cp.is_processed_msg(book_msg.get_id()):
            return

        self.counter.add_book(book_msg.get_book())

    def process_review(self, review_msg: ReviewMessage):
        review = review_msg.get_review()
        author, title, avg = self.counter.add_review(review)

        result = []
        if not title:
            return

        if title not in self.sent_titles:
            self.sent_titles.add(title)
            authors_msg = TitleAuthorsMessage(
                title, author, *review_msg.get_headers())
            result.append(authors_msg)

        title_score_msg = TitleScoreMessage(
            title, avg, *review_msg.get_headers())

        result.append(title_score_msg)

    def send_to_next_worker(self, result):
        for msg in result:
            next_pool_name = ''
            if msg.get_identifier() == TITLE_SCORE:
                next_pool_name = '500_reviews'
            elif msg.get_identifier() == TITLE_AUTHORS:
                next_pool_name = 'results'

            self.queue_middleware.send_to_pool(
                encode(msg), msg.get_title(), next_pool_name=next_pool_name)

    def process_query_message(self, msg):
        if msg.get_identifier() == BOOK:
            return self.process_book(msg)
        elif msg.get_identifier() == REVIEW:
            return self.process_review(msg)
