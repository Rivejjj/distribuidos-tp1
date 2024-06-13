import logging
from entities.book import Book
from entities.query_message import QueryMessage


class BookMessage(QueryMessage):
    def __init__(self, book: Book, identifier: int, id: str, client_id: str, query=None):
        self.book = book
        super().__init__(identifier, id, client_id, query)

    def get_book(self):
        return self.book

    def serialize_data(self) -> str:
        return str(self.book)
