import unittest
from common.reviews_counter import ReviewsCounter
from messages.book import Book
from messages.review import Review

class TestUtils(unittest.TestCase):
    base_book = Book('distributed systems', 'description', 'authors', 'image', 'preview_link', 'publisher',2019, 'info_link', ['category', 'category2'], 'ratings_count')

    base_review = Review(1,'distributed systems', 10, 1, 'profile_name', 'helpfulness', 5, 'time', 'summary', 'text')

    
    def test_add_review(self):
        counter = ReviewsCounter()

        new_review = Review(1,'distributed systems', 10, 1, 'profile_name', 'helpfulness', 2, 'time', 'summary', 'text')

        counter.add_review(self.base_review)
        self.assertEqual(counter.reviews['distributed systems'], (1, 5))

        counter.add_review(self.base_review)
        self.assertEqual(counter.reviews['distributed systems'], (2, 5))

        counter.add_review(new_review)
        self.assertEqual(counter.reviews['distributed systems'], (3, 4))

    def test_add_book(self):
        counter = ReviewsCounter()

        counter.add_book(self.base_book)
        self.assertEqual(counter.books['distributed systems'], self.base_book)

        new_book = Book('distributed systems 2', 'description', 'authors', 'image', 'preview_link', 'publisher',2019, 'info_link', ['category', 'category2'], 'ratings_count')
        counter.add_book(new_book)
        self.assertEqual(counter.books['distributed systems 2'], new_book)