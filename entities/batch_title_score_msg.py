from entities.query_message import BATCH_TITLE_SCORE, QueryMessage
from utils.parser import DATA_SEPARATOR
from typing import List, Tuple

TitleScore = Tuple[str, float]


class BatchTitleScoreMessage(QueryMessage):
    def __init__(self, content: List[TitleScore], id: str, client_id: str, query=None):
        self.content = content
        super().__init__(BATCH_TITLE_SCORE, id, client_id, query)

    def serialize_data(self) -> str:
        title_score_str = map(
            lambda title, score: f"{title}{DATA_SEPARATOR}{score}", self.content)
        return "\n".join(title_score_str)
