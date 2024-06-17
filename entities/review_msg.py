from entities.query_message import REVIEW, QueryMessage
from entities.review import Review


class ReviewMessage(QueryMessage):
    def __init__(self, review: Review, id: str, client_id: str):
        self.review = review
        super().__init__(REVIEW, id, client_id)

    def get_review(self):
        return self.review

    def serialize_data(self) -> str:
        return str(self.review)
