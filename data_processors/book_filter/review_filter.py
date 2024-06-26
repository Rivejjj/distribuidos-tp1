

from entities.query_message import QueryMessage
from entities.review import Review


class ReviewFilter:
    def __init__(self):
        self.titles = {}  # client_id: set()

    def add_title(self, title: str, client_id: int):
        self.titles[client_id] = self.titles.get(client_id, set())

        self.titles[client_id].add(title)

    def filter(self, review: Review, client_id: int) -> bool:
        return review.title in self.titles.get(client_id, set())

    def clear(self, msg: QueryMessage):
        client_id = msg.get_client_id()
        if client_id in self.titles:
            self.titles.pop(client_id)
