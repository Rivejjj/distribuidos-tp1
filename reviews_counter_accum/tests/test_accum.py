import unittest
from common.reviews_counter import ReviewsCounter
from messages.book import Book
from messages.review import Review
from gateway.common.data_receiver import DataReceiver

class TestUtils(unittest.TestCase):
    book_line = """distributed systems, description,['authors'], image, preview_link, publisher,2019, info_link, "['category', 'category2']", ratings_count"""

    review_line = "1,distributed systems, 10, 1, profile_name, helpfulness, 5, time, summary, text"

    
    # def test_add_review(self):
    #     counter = ReviewsCounter()
    #     data_receiver = DataReceiver()
    #     new_review = data_receiver.parse_review(self.review_line)

    #     counter.add_review(new_review)
    #     self.assertEqual(counter.reviews['distributed systems'], (1, 5))

    #     counter.add_review(new_review)
    #     self.assertEqual(counter.reviews['distributed systems'], (2, 5))

    #     new_review.score = 2
    #     counter.add_review(new_review)
    #     self.assertEqual(counter.reviews['distributed systems'], (3, 4))

    def test_add_book(self):
        counter = ReviewsCounter()
        data_receiver = DataReceiver()
        book = data_receiver.parse_book(self.book_line)
        counter.add_book(book)

        self.assertEqual(counter.books['distributed systems'], book)

        new_book_line = """distributed systems 2, description,['authors'], image, preview_link, publisher,2019, info_link, "['category', 'category2']", ratings_count"""

        new_book = data_receiver.parse_book(new_book_line)
        counter.add_book(new_book)
        self.assertEqual(counter.books['distributed systems 2'], new_book)