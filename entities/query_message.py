BOOK = 1
REVIEW = 2
TITLE_AUTHORS = 3
AUTHORS = 4
TITLE_SCORE = 5
QUERY_MSG_SEPARATOR = ";"


class QueryMessage:
    def __init__(self, identifier, data):
        self.identifier = identifier
        self.data = data

    def get_data(self):
        return self.data

    def get(self):
        return self.identifier

    def __str__(self):
        return f"{self.identifier}{QUERY_MSG_SEPARATOR}{self.data}"
