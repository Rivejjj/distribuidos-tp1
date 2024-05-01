import unittest
from common.accumulator import Accumulator
from messages.book import Book
from messages.review import Review

class TestUtils(unittest.TestCase):
    book = ["a","2.0"]

    def test_get_year_regex(self):
        accum = Accumulator(10)
        accum.add_book(self.book)
        self.assertEqual(accum.books["a"], 2.0)