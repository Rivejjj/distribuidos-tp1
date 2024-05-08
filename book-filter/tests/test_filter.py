import unittest
from common.book_filter import BookFilter
from messages.book import Book


class TestUtils(unittest.TestCase):
    base_book = Book('distributed systems', 'authors', 'publisher',
                     '2019',  "['category', 'category2']")

    def test_filter_by_category(self):
        book_filter = BookFilter(category='category')
        self.assertTrue(book_filter.filter(self.base_book))

        book_filter = BookFilter(category='category2')
        self.assertTrue(book_filter.filter(self.base_book))

        book_filter = BookFilter(category='category3')
        self.assertFalse(book_filter.filter(self.base_book))

    def test_filter_by_published_year(self):
        book_filter = BookFilter(published_year_range=(2019, 2019))
        self.assertTrue(book_filter.filter(self.base_book))

        book_filter = BookFilter(published_year_range=(2018, 2019))
        self.assertTrue(book_filter.filter(self.base_book))

        book_filter = BookFilter(published_year_range=(2020, 2020))
        self.assertFalse(book_filter.filter(self.base_book))

    def test_filter_by_title(self):
        book_filter = BookFilter(title_contains='distributed')
        self.assertTrue(book_filter.filter(self.base_book))

        book_filter = BookFilter(title_contains='distributed systems')
        self.assertTrue(book_filter.filter(self.base_book))

        book_filter = BookFilter(title_contains='systems')
        self.assertTrue(book_filter.filter(self.base_book))

        book_filter = BookFilter(title_contains='distributed systems ')
        self.assertFalse(book_filter.filter(self.base_book))

        book_filter = BookFilter(title_contains='distributed systems and')
        self.assertFalse(book_filter.filter(self.base_book))


    def test_contains_category_fiction(self):
        book_filter = BookFilter(category='fiction')
        self.assertFalse(book_filter.filter(self.base_book))

        fiction_book = Book('distributed systems', 'authors', 'publisher',
                            '2019',  "['juvenile nonfiction']")
        self.assertTrue(book_filter.filter(fiction_book))

    def test_caregory_is_equal(self):
        filter = BookFilter(category='Computers', is_equal=True)
        self.assertFalse(filter.filter(self.base_book))

        computers_book = Book('distributed systems', 'authors', 'publisher',
                              '2019',  "['Computers']")
        self.assertTrue(filter.filter(computers_book))


if __name__ == '__main__':
    unittest.main()
