from messages.book import Book
from messages.review import Review
from parser_1.csv_parser import CsvParser

CATEGORIES_POSITION = 8
CATEGORIES_SEPARATOR = ';'

class DataReceiver:
    def __init__(self):
        pass

    def parse_book(self, data):
        parser = CsvParser()
        #print("Processing message: %s", line)
        line = parser.parse_csv(data)

        line[CATEGORIES_POSITION] = line[CATEGORIES_POSITION].split(CATEGORIES_SEPARATOR)
        
        book = Book(*line)
        if book.sanitize():
            return book

    def parse_review(self, data): #tambien esta mal
        review_fields = data.split(',')
        if len(review_fields) != 10:
            raise ValueError("Invalid review data")
    
        return Review(*review_fields)
    
    def text_to_q1(self, line):
        book = self.parse_book(line)
        if book:
            return f"{book.title},,{book.authors},,,{book.publisher},{book.published_year},,{book.categories},"
        return None