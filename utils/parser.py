import csv
import json
from entities.authors_msg import AuthorsMessage
from entities.book import Book
from entities.book_msg import BookMessage
from entities.eof_msg import EOFMessage
from entities.query_message import AUTHORS, BOOK, EOF, QUERY_MSG_SEPARATOR, REVIEW
from entities.review import Review
from entities.review_msg import ReviewMessage
from utils.initialize import decode

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


def split_line(line, delimiter=","):
    res = list(csv.reader([line], delimiter=delimiter))[0]
    return res


def parse_client_msg(msg):
    identifier, data = msg.split(QUERY_MSG_SEPARATOR, 1)
    return int(identifier), data


def parse_query_msg(msg: bytes):
    print(decode(msg).split(QUERY_MSG_SEPARATOR, 1))
    header, data = decode(msg).split(QUERY_MSG_SEPARATOR, 1)

    header = json.loads(header)

    identifier = int(header[0])

    if identifier == BOOK:
        return BookMessage(parse_book(data), *header)
    elif identifier == REVIEW:
        return ReviewMessage(parse_review(data), *header)
    elif identifier == AUTHORS:
        return AuthorsMessage(*data.split(DATA_SEPARATOR), *header)
    elif identifier == EOF:
        return EOFMessage(*header)
    else:
        raise Exception('Mensaje desconocido')
