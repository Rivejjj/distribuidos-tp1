import unittest
from common.accumulator import Accumulator
from messages.book import Book
from messages.review import Review
from gateway.common.data_receiver import DataReceiver


class TestUtils(unittest.TestCase):
    book_like = "distributed systems, description,['authors'], image, preview_link, publisher,2019, info_link, ['category', 'category2'], ratings_count"

    review_line = "1,distributed systems, 10, 1, profile_name, helpfulness, 5, time, summary, text"

    def assertTrue(self):
        self.assertTrue(True)

    '''
    def test_get_year_regex(self):
        acum = Accumulator()
        self.assertEqual(acum.get_year_regex(''), None)
        self.assertEqual(acum.get_year_regex('2019'), 2019)
        self.assertEqual(acum.get_year_regex('2019-20-03'), 2019)
        self.assertEqual(acum.get_year_regex('20-03-2019'), 2019)
        self.assertEqual(acum.get_year_regex('20-03-19'), None)
        self.assertEqual(acum.get_year_regex('01/01/2019'), 2019)

    def test_get_decade(self):
        acum = Accumulator()
        self.assertEqual(acum.get_decade(2019), 2010)
        self.assertEqual(acum.get_decade(2020), 2020)
        self.assertEqual(acum.get_decade(1991), 1990)
        self.assertEqual(acum.get_decade(None),None)

    def test_add_author(self):
        acum = Accumulator()
        acum.add_author('author1', 2010)
        self.assertEqual(acum.authors['author1'][2010], 1)
        acum.add_author('author1', 2010)
        self.assertEqual(acum.authors['author1'][2010], 2)
        acum.add_author('author1', 2020)
        self.assertEqual(acum.authors['author1'][2020], 1)
        acum.add_author('author2', 2020)
        self.assertEqual(acum.authors['author2'][2020], 1)
    '''
    # def test_add_book(self):
    #     book = DataReceiver().parse_book(self.line)
    #     accum = Accumulator()
    #     accum.add_book(book)
    #     self.assertEqual(accum.authors['authors'][2010], 1)
    #     accum.add_book(book)
    #     self.assertEqual(accum.authors['authors'][2010], 2)
