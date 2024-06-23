

from entities.book import Book
from entities.query_message import QueryMessage


class Accumulator:
    def __init__(self):
        self.authors = {}  # client -> author -> {decade -> count}
        self.completed_authors = {}  # client -> completed_authors (set)

    def add_book(self, book: Book, client_id: int):
        year = int(book.published_year)
        if year is None:
            return
        decade = self.__get_decade(year)
        self.__add_author(book.authors, decade, client_id)

        return self.check_valid_author(book.authors, client_id)

    def check_valid_author(self, author: str, client_id: int):
        client_id = int(client_id)
        self.completed_authors[client_id] = self.completed_authors.get(
            client_id, set())

        if author in self.completed_authors[client_id]:
            return False

        result = len(self.authors[client_id][author]) >= 10
        if result:
            self.completed_authors[client_id].add(author)
            self.authors[client_id].pop(author)
        return result

    def __add_author(self, author: str, decade: int, client_id: int):
        self.authors[client_id] = self.authors.get(client_id, {})

        self.authors[client_id][author] = self.authors[client_id].get(
            author, set())

        self.authors[client_id][author].add(decade)

    def __get_decade(self, year):
        return year // 10 * 10

    def clear(self, msg: QueryMessage):
        client_id = msg.get_client_id()
        self.authors.pop(client_id)
        self.completed_authors.pop(client_id)
