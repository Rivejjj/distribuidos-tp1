from messages.book import Book
from messages.review import Review

CATEGORIES_POSITION = 8
CATEGORIES_SEPARATOR = ';'

class DataReceiver:
    def __init__(self, client = None):
        self.client = client 


    def receive(self):
        data = self.client.recv()
        return data
    
    def parse_book(self, data):
        book_fields = data.split(',')
        if len(book_fields) != 10:
            raise ValueError("Invalid book data")
        
        book_fields[CATEGORIES_POSITION] = book_fields[CATEGORIES_POSITION].split(CATEGORIES_SEPARATOR)
        
        return Book(*book_fields)

    def parse_review(self, data):
        review_fields = data.split(',')
        if len(review_fields) != 10:
            raise ValueError("Invalid review data")
    
        return Review(*review_fields)