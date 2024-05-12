from decades_accumulator.common.accumulator import Accumulator
from gateway.common import data_receiver
from messages.book import Book


def main():
    data = data_receiver.DataReceiver()
    accumulator = Accumulator()
    with open('data/books_data.csv', 'r') as a, open('tests/test_results.csv', 'w') as r:
        for line in a:
            book = data.parse_book(line)
            if not book:
                continue

            books = Book.expand_authors(book)
            for book in books:
                if 'Karl Marx' in book.authors:
                    print(book.published_year)
                # if accumulator.add_book(book):
                #     r.write(f"{book.authors}\n")
                #     print(
                #         f"Author {book.authors} has more than 10 books in a decade.")


main()
