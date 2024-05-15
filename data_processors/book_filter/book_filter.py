from entities.book import Book
import logging

class BookFilter:
    def __init__(self, category=None, published_year_range=None, title_contains=None, is_equal=None):
        self.category = category
        self.is_equal = is_equal
        self.published_year_range = published_year_range
        self.title_contains = title_contains

        if not self.category and not self.published_year_range and not self.title_contains:
            raise ValueError("At least one filter must be provided")

    def filter(self, book) -> bool:
        if self.category:
            return self.__filter_by_category(book)

        if self.published_year_range:
            return self.__filter_by_published_year(book)

        if self.title_contains:
            return self.__filter_by_title(book)

        raise ValueError("No filter criteria was provided")

    def __filter_by_category(self, book) -> bool:
        result = False
        if self.is_equal:
            result = self.__is_equal(book.categories)
        else:
            result = self.category in book.categories

        if result:
            logging.info(f"Book accepted: {book.title}, {book.categories}")
            book.categories = None
        return result

    def __filter_by_published_year(self, book) -> bool:
        result = self.published_year_range[0] <= int(
            book.published_year) <= self.published_year_range[1]

        if result:
            book.published_year = None

        return result

    def __filter_by_title(self, book) -> bool:
        return self.title_contains.lower() in book.title.lower()

    def __is_equal(self, book_categories):
        categories = book_categories.strip('"[]').replace("'", "")
        return categories == self.category
