from entities.query_message import TITLE_SCORE, QueryMessage
from utils.parser import DATA_SEPARATOR


class TitleScoreMessage(QueryMessage):
    def __init__(self, title: str, score: float, id: str, client_id: str, query=None):
        self.title = title
        self.score = score
        super().__init__(TITLE_SCORE, id, client_id, query)

    def get_title(self):
        return self.title

    def get_score(self):
        return self.score

    def serialize_data(self) -> str:
        return DATA_SEPARATOR.join([self.title, str(self.score)])
