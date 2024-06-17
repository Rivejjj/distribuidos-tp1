import csv
import json
import logging
from entities.authors_msg import AuthorsMessage
from entities.batch_title_score_msg import BatchTitleScoreMessage
from entities.book import Book
from entities.book_msg import BookMessage
from entities.eof_msg import EOFMessage
from entities.query_message import AUTHORS, BATCH_TITLE_SCORE, BOOK, EOF, QUERY_MSG_SEPARATOR, REVIEW, TITLE_AUTHORS, TITLE_SCORE
from entities.review import Review
from entities.review_msg import ReviewMessage
from entities.title_authors_msg import TitleAuthorsMessage
from entities.title_score_msg import TitleScoreMessage
from utils.initialize import decode
from utils.to_str import DATA_SEPARATOR


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
    header, data = decode(msg).split(QUERY_MSG_SEPARATOR, 1)

    logging.info(f"{header} {data}")

    header = json.loads(header)

    identifier = int(header[0])

    header.pop(0)

    if identifier == BOOK:
        return BookMessage(parse_book(data), *header)
    elif identifier == REVIEW:
        return ReviewMessage(parse_review(data), *header)
    elif identifier == TITLE_AUTHORS:
        return TitleAuthorsMessage(*data.split(DATA_SEPARATOR), *header)
    elif identifier == AUTHORS:
        return AuthorsMessage(*data.split(DATA_SEPARATOR), *header)
    elif identifier == TITLE_SCORE:
        return TitleScoreMessage(*data.split(DATA_SEPARATOR), *header)
    elif identifier == EOF:
        return EOFMessage(*header)
    elif identifier == BATCH_TITLE_SCORE:
        return BatchTitleScoreMessage(*data.split(DATA_SEPARATOR), *header)
    else:
        raise Exception('Mensaje desconocido')
