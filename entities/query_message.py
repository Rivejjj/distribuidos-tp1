from abc import ABC, abstractmethod
import json


BOOK = 1
REVIEW = 2
TITLE_AUTHORS = 3
AUTHORS = 4
TITLE_SCORE = 5
EOF = 6
QUERY_MSG_SEPARATOR = ";"


class QueryMessage(ABC):
    def __init__(self,  identifier, id, client_id, query=None):
        self.identifier = identifier
        self.id = id
        self.client_id = client_id
        self.query = query

    def get_client_id(self):
        return self.client_id

    def get_id(self):
        return self.id

    def get_identifier(self):
        return self.identifier

    def get_query(self):
        return self.query

    @abstractmethod
    def serialize_data(self) -> str:
        pass

    def __str__(self):
        headers = [self.identifier, self.id, self.client_id]
        if self.query:
            headers.append(self.query)
        return f"{QUERY_MSG_SEPARATOR.join([json.dumps(headers), self.serialize_data()])}"

    def is_eof(self) -> bool:
        return self.identifier == EOF
