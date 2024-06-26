from data_processors.data_manager.data_manager import DataManager
from book_authors_cp import BookAuthorsCheckpoint
from entities.book import Book
from entities.client_dc import ClientDCMessage
from sent_titles_cp import SentTitlesCheckpoint
from reviews_counter_cp import ReviewsCounterCheckpoint
from reviews_counter import ReviewsCounter
from entities.book_msg import BookMessage
from entities.query_message import BOOK, REVIEW, TITLE_AUTHORS, TITLE_SCORE, QueryMessage
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

        self.sent_titles_cp = SentTitlesCheckpoint()

    def process_book(self, book_msg: BookMessage):
        if self.messages_cp.is_processed_msg(book_msg):
            return

        book = book_msg.get_book()
        self.counter.add_book(book, book_msg.get_client_id())
        self.book_authors_cp.save(book, book_msg.get_client_id())

    def process_review(self, review_msg: ReviewMessage):
        review = review_msg.get_review()

        author, title, avg = None, None, None

        msg_already_processed = self.messages_cp.is_processed_msg(
            review_msg)

        client_id = review_msg.get_client_id()

        if msg_already_processed:
            author, title, avg = self.counter.get_review(review, client_id)
        else:
            author, title, avg = self.counter.add_review(review, client_id)
            self.reviews_counter_cp.save(review, client_id)

        result = []
        if not self.counter.review_more_than_min(review, client_id):
            return

        if self.sent_titles_cp.not_sent(title, client_id):
            if not msg_already_processed:
                self.sent_titles_cp.save(title, client_id)
            authors_msg = TitleAuthorsMessage(
                title, author, *review_msg.get_headers(), self.query)
            result.append(authors_msg)

        title_score_msg = TitleScoreMessage(
            title, avg, *review_msg.get_headers())

        result.append(title_score_msg)

        return result

    def send_to_next_worker(self, result: list[QueryMessage]):
        for msg in result:
            next_pool_name = ''
            if msg.get_identifier() == TITLE_SCORE:
                next_pool_name = '500_reviews'
            elif msg.get_identifier() == TITLE_AUTHORS:
                next_pool_name = 'results'

            if msg.get_query():
                self.queue_middleware.send_to_result(msg)
            else:
                self.queue_middleware.send_to_pool(
                    encode(msg), msg.get_title(), next_pool_name=next_pool_name)

    def process_query_message(self, msg):
        if msg.get_identifier() == BOOK:
            return self.process_book(msg)
        elif msg.get_identifier() == REVIEW:
            return self.process_review(msg)

    def delete_client(self, msg: ClientDCMessage):
        self.book_authors_cp.delete_client(msg)
        self.counter.clear(msg)
        self.reviews_counter_cp.delete_client(msg)
        self.sent_titles_cp.delete_client(msg)
        return super().delete_client(msg)
