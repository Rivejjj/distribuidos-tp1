BOOK_IDENTIFIER = 0
REVIEW_IDENTIFIER = 1


class QueryMessage:
    def __init__(self, book=None, review=None):
        self.book = book
        self.review = review

        if book:
            self.type = BOOK_IDENTIFIER
        elif review:
            self.type = REVIEW_IDENTIFIER

    def get_entity(self):
        if self.type == BOOK_IDENTIFIER:
            return self.book
        elif self.type == REVIEW_IDENTIFIER:
            return self.review

    def is_book(self):
        return self.type == BOOK_IDENTIFIER

    def is_review(self):
        return self.type == REVIEW_IDENTIFIER

    def __str__(self):
        return f"{self.type}:{self.get_entity()}"
