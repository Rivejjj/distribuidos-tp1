from entities.query_message import QueryMessage
from entities.review import Review


class ReviewMessage(QueryMessage):
    def __init__(self, review: Review, identifier: int, id: str, client_id: str):
        self.review = review
        super().__init__(id, identifier, client_id)

    def get_review(self):
        return self.review

    def serialize_data(self) -> str:
        return str(self.review)
