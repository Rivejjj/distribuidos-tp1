
from entities.book import Book
from entities.review import Review


import re

from utils.parser import split_line

year_regex = re.compile('[^\d]*(\d{4})[^\d]*')


CATEGORIES_POSITION = 8
CATEGORIES_SEPARATOR = ';'

TOTAL_FIELDS_COUNT = 10


def get_year_regex(text):
    if text:
        result = year_regex.search(text)
        return int(result.group(1)) if result else None
    return None


def parse_book_from_client(data):
    line = split_line(data)

    title, authors, publisher, published_year, categories = line[
        0], line[2], line[5], line[6], line[8]

    published_year = get_year_regex(published_year)

    for field in [title, authors, published_year, categories]:
        if not field:
            return None

    return Book(title, authors, publisher, published_year, categories)


def validate_review(title, score, text):
    return title and score and text


def parse_review_from_client(data):
    line = split_line(data)

    title, score, text = line[1], line[6], line[9]

    return Review(title, score, text)
