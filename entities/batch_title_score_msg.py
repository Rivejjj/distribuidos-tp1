from entities.query_message import BATCH_TITLE_SCORE, QueryMessage
from typing import List, Tuple

from utils.to_str import to_str

TitleScore = Tuple[str, float]


class BatchTitleScoreMessage(QueryMessage):
    def __init__(self, content: List[TitleScore], id: str, client_id: str, query=None):
        self.content = content
        super().__init__(BATCH_TITLE_SCORE, id, client_id, query)

    def serialize_data(self) -> str:
        title_score_str = map(
            lambda titlescore: to_str(titlescore), self.content)
        return "\n".join(title_score_str)
