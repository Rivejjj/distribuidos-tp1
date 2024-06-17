from entities.query_message import TITLE_AUTHORS, QueryMessage
from utils.to_str import to_str


class TitleAuthorsMessage(QueryMessage):
    def __init__(self, title: str, authors: str, id: str, client_id: str, query=None):
        self.title = title
        self.authors = authors
        super().__init__(TITLE_AUTHORS, id, client_id, query)

    def get_title(self):
        return self.title

    def get_authors(self):
        return self.authors

    def serialize_data(self) -> str:
        return to_str([self.title, self.authors])
