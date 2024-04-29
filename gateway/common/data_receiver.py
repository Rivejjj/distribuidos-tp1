from messages.book import Book
from messages.review import Review
import csv

CATEGORIES_POSITION = 8
CATEGORIES_SEPARATOR = ';'


class DataReceiver:
    def __init__(self):
        pass

    def parse_book(self, data):

        # CAMBIAR ESTO PARA USAR CSV READER:
        # CUANDO LAS DESCRIPCIONES TIENEN COMA NO FUNCIONA, PORQUE OBVIAMENTE VAN A TENER
        # MAS DE 10 CAMPOS (LINEA 19)

        book_fields = data.split(',')
        if len(book_fields) != 10:
            # print("NOT 10 FIELDS: ", book_fields)
            # for field in book_fields:
            #     print(field)
            return None

        book_fields[CATEGORIES_POSITION] = book_fields[CATEGORIES_POSITION].split(
            CATEGORIES_SEPARATOR)

        book = Book(*book_fields)
        if book.sanitize():
            return book

    def parse_review(self, data):
        review_fields = data.split(',')
        if len(review_fields) != 10:
            raise ValueError("Invalid review data")

        return Review(*review_fields)
