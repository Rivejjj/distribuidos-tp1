from abc import ABC, abstractmethod
import json


BOOK = 1
REVIEW = 2
TITLE_AUTHORS = 3
AUTHORS = 4
TITLE_SCORE = 5
EOF = 6
BATCH_TITLE_SCORE = 7
CLIENT_DC = 8
QUERY_MSG_SEPARATOR = ";"


class QueryMessage(ABC):
    def __init__(self,  identifier, id, client_id, query=None):
        self.identifier = identifier
        self.id = id
        self.client_id = client_id
        self.query = query

    def get_client_id(self) -> int:
        return self.client_id

    def get_id(self) -> int:
        return self.id

    def get_identifier(self) -> int:
        return self.identifier

    def get_query(self):
        return self.query

    def get_headers(self):
        """
        Devuelve el id, id del cliente y la query que contiene el mensaje
        """
        headers = [self.id, self.client_id]
        if self.query:
            headers.append(self.query)

        return headers

    @abstractmethod
    def serialize_data(self) -> str:
        """
        Representacion de string de la data que contiene el mensaje
        """
        pass

    def __str__(self):
        headers = self.get_headers()
        headers.insert(0, self.identifier)
        return f"{QUERY_MSG_SEPARATOR.join([json.dumps(headers), self.serialize_data()])}"

    def is_eof(self) -> bool:
        return self.identifier == EOF

    def is_dc(self) -> bool:
        return self.identifier == CLIENT_DC
