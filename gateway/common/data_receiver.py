from messages.book import Book
from messages.review import Review
from parser_1.csv_parser import CsvParser

CATEGORIES_POSITION = 8
CATEGORIES_SEPARATOR = ';'

TOTAL_FIELDS_COUNT = 10
BOOKS_FIELDS_COUNT = 5
REVIEW_FIELDS_COUNT = 3

class DataReceiver:
    def __init__(self):
        pass

    def parse_book(self, data):
        parser = CsvParser()
        # print("Processing message: %s", line)
        line = parser.parse_csv(data)

        if len(line) != TOTAL_FIELDS_COUNT and len(line) != BOOKS_FIELDS_COUNT:
            return None
        
        if len(line) == TOTAL_FIELDS_COUNT:
            line[CATEGORIES_POSITION] = line[CATEGORIES_POSITION].split(CATEGORIES_SEPARATOR)
            title, authors, publisher, published_year, categories = line[
            0], line[2], line[5], line[6], line[8]

        if len(line) == BOOKS_FIELDS_COUNT: 
            title, authors, publisher, published_year, categories = line[
            0], line[1], line[2], line[3], line[4]

        book = Book(title, authors, publisher, published_year, categories)
        if book.sanitize():
            return book
        return None

    def parse_review(self, data):
        parser = CsvParser()
        # print("Processing message: %s", line)
        line = parser.parse_csv(data)

        if len(line) != TOTAL_FIELDS_COUNT and len(line) != REVIEW_FIELDS_COUNT:
            return None

        if len(line) == TOTAL_FIELDS_COUNT:
            title, score, text = line[1], line[6], line[9]

        if len(line) == REVIEW_FIELDS_COUNT:
            title, score, text = line[0], line[1], line[2]

        review = Review(title, score, text)
        if review.sanitize():
            return review
        return None
