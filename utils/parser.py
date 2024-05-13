import csv
from entities.book import Book
from entities.query_message import QUERY_MSG_SEPARATOR
from entities.review import Review

DATA_SEPARATOR = "\t"


def parse_book(data):
    line = data.split(DATA_SEPARATOR)
    title = line[0].strip()
    authors = line[1].strip()
    publisher = line[2].strip()
    published_year = line[3].strip()
    categories = line[4].strip()
    return Book(title, authors, publisher, published_year, categories)


def parse_review(data):
    line = data.split(DATA_SEPARATOR)
    return Review(*line)


def parse_query_msg(data):
    identifier, rest = data.split(QUERY_MSG_SEPARATOR, 1)

    return int(identifier), rest


def split_line(line, delimiter=","):
    res = list(csv.reader([line], delimiter=delimiter))[0]
    return res
