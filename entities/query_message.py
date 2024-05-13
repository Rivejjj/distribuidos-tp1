ANY_IDENTIFIER = 0
BOOK_IDENTIFIER = 1
REVIEW_IDENTIFIER = 2
QUERY_MSG_SEPARATOR = ";"


class QueryMessage:
    def __init__(self, identifier, data):
        self.identifier = identifier
        self.data = data

    def get_data(self):
        return self.data

    def get_identifier(self):
        return self.identifier

    def __str__(self):
        return f"{self.identifier}{QUERY_MSG_SEPARATOR}{self.data}"
