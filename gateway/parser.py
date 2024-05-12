import csv

from entities.book import Book
from entities.review import Review

CATEGORIES_POSITION = 8
CATEGORIES_SEPARATOR = ';'

TOTAL_FIELDS_COUNT = 10


def parse_book_from_client(data):
    # print("Processing message: %s", line)
    line = list(csv.reader([data]))[0]

    if len(line) != TOTAL_FIELDS_COUNT:
        return None

    line[CATEGORIES_POSITION] = line[CATEGORIES_POSITION].split(
        CATEGORIES_SEPARATOR)

    title, authors, publisher, published_year, categories = line[
        0], line[2], line[5], line[6], line[8]

    book = Book(title, authors, publisher, published_year, categories)

    if book.sanitize():
        return book


def parse_review_from_client(data):
    line = list(csv.reader([data]))[0]

    if len(line) != TOTAL_FIELDS_COUNT:
        return None

    title, score, text = line[1], line[6], line[9]
    review = Review(title, score, text)

    if review.sanitize():
        return review
