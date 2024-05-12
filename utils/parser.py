import csv
from entities.book import Book
from entities.query_message import QUERY_MSG_SEPARATOR
from entities.review import Review


def parse_book(data):
    line = split_line(data, "|")

    return Book(*line)


def parse_review(data):
    line = split_line(data, "|")
    return Review(*line)


def parse_query_msg(data):
    identifier, rest = data.split(QUERY_MSG_SEPARATOR, 1)

    return int(identifier), rest


def split_line(line, delimiter=","):
    res = list(csv.reader([line], delimiter=delimiter))[0]
    return res
