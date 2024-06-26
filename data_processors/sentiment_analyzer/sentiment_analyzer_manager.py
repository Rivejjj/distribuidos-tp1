from data_processors.data_manager.data_manager import DataManager
from entities.client_dc import ClientDCMessage
from sentiment_analyzer import SentimentAnalyzer
from entities.query_message import REVIEW, QueryMessage
from entities.title_score_msg import TitleScoreMessage
from entities.review_msg import ReviewMessage
from utils.initialize import encode


class SentimentAnalyzerManager(DataManager):
    def __init__(self, config_params):
        super().__init__(config_params)
        self.analyzer = SentimentAnalyzer()

    def run(self):
        self.queue_middleware.start_consuming(
            self.process_message())

    def process_review(self, review_msg: ReviewMessage):
        review = review_msg.get_review()
        polarity_score = self.analyzer.analyze(review.text)

        return TitleScoreMessage(review.title, polarity_score, *review_msg.get_headers(), self.query)

    def send_to_next_worker(self, msg):
        self.queue_middleware.send_to_pool(
            encode(msg), msg.get_title())

    def process_query_message(self, msg):
        if msg.get_identifier() == REVIEW:
            return self.process_review(msg)
