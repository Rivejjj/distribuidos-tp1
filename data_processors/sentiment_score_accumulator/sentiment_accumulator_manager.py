from data_processors.data_manager.data_manager import DataManager
from entities.batch_title_score_msg import BatchTitleScoreMessage
from sentiment_score_accumulator import SentimentScoreAccumulator
from entities.query_message import REVIEW, TITLE_SCORE
from entities.title_score_msg import TitleScoreMessage
from entities.review_msg import ReviewMessage
from utils.initialize import encode, uuid


class SentimentAccumulatorManager(DataManager):
    def __init__(self, config_params):
        super().__init__(config_params)
        self.acc = SentimentScoreAccumulator()

    def run(self):
        self.queue_middleware.start_consuming(
            self.process_message())

    def eof_cb(self, msg):
        msg = BatchTitleScoreMessage(
            self.acc.calculate_90th_percentile(), uuid(), msg.get_client_id(), self.query)
        self.queue_middleware.send_to_all(encode(msg))
        self.acc.clear()

    def process_title_score(self, title_score_msg: TitleScoreMessage):
        self.acc.add_sentiment_score(
            title_score_msg.get_title(), title_score_msg.get_score())

    def send_to_next_worker(self, msg):
        self.queue_middleware.send_to_pool(
            encode(msg), msg.get_title())

    def process_query_message(self, msg):
        if msg.get_identifier() == TITLE_SCORE:
            return self.process_title_score(msg)
