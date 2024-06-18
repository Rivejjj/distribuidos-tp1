from entities.book import Book
from entities.query_message import AUTHORS, QueryMessage


class AuthorsMessage(QueryMessage):
    def __init__(self, author: str, id: str, client_id: str, query=None):
        self.author = author
        super().__init__(AUTHORS, id, client_id, query)

    def get_author(self):
        return self.author

    def serialize_data(self) -> str:
        return self.get_author()
