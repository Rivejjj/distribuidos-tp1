from data_processors.sentiment_analyzer.sentiment_analyzer import SentimentAnalizer
from data_processors.sentiment_score_accumulator.sentiment_score_accumulator import SentimentScoreAccumulator
from entities.query_message import ANY_IDENTIFIER, QueryMessage
from gateway.client_parser import parse_book_from_client, parse_review_from_client
from utils.parser import parse_book, parse_query_msg, parse_review, split_line
from data_processors.book_filter.book_filter import BookFilter


def generate_review(book):
    query_message = QueryMessage(ANY_IDENTIFIER, book)

    _, data = parse_query_msg(str(query_message))

    return parse_review(data)


def generate_book(data):
    query_message = QueryMessage(ANY_IDENTIFIER, data)

    _, data = parse_query_msg(str(query_message))

    return parse_book(data)


def main():
    with open('data/csv/Books_rating.csv', 'r') as reviews, open('data/csv/books_data.csv', 'r') as books, open('query5.csv', 'w') as w:
        analyzer = SentimentAnalizer()
        accumulator = SentimentScoreAccumulator()
        fiction_filter = BookFilter(category='fiction')
        valid_books = set()

        for line in books:
            book = parse_book_from_client(line)

            if not book:
                continue

            if fiction_filter.filter(book):
                valid_books.add(book.title)

        for line in reviews:
            review = parse_review_from_client(line)

            if review.title not in valid_books:
                continue
            if not review.text:
                continue
            result = analyzer.analyze(review.text)

            if result is None:
                continue

            accumulator.add_sentiment_score(review.title, result)

        for title, score in accumulator.calculate_90th_percentile():
            w.write(f"{title},{score}\n")


main()
