import unittest
from common.book_filter import BookFilter
from messages.book import Book


class TestUtils(unittest.TestCase):
    base_book = Book('distributed systems', 'description', 'authors', 'image', 'preview_link', 'publisher',
                     2019, 'info_link', ['category', 'category2'], 'ratings_count')

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


if __name__ == '__main__':
    unittest.main()
