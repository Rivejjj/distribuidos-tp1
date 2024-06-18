

from data_processors.data_manager.data_manager import DataManager
from entities.batch_title_score_msg import BatchTitleScoreMessage
from entities.query_message import TITLE_SCORE
from entities.title_score_msg import TitleScoreMessage
from top_rating_cp import TopRatingCheckpoint
from top_rating_accumulator import TopRatingAccumulator
from utils.initialize import encode, uuid


class TopRatingManager(DataManager):
    def __init__(self, config_params):
        super().__init__(config_params)
        self.acc = TopRatingAccumulator()
        self.cp = TopRatingCheckpoint(self.acc)

    def eof_cb(self, msg):
        msg = BatchTitleScoreMessage(
            self.acc.get_top(), uuid(), msg.get_client_id(), self.query)
        self.queue_middleware.send_to_all(encode(msg))
        self.acc.clear()

    def process_title_score(self, title_score_msg: TitleScoreMessage):
        title, score = title_score_msg.get_title(), title_score_msg.get_score()
        if self.messages_cp.is_processed_msg(title_score_msg.get_id()):
            return
        self.acc.add_title(
            title, score)
        self.cp.save(title, score)

    def send_to_next_worker(self, msg):
        return

    def process_query_message(self, msg):
        if msg.get_identifier() == TITLE_SCORE:
            return self.process_title_score(msg)
