from parser_1.csv_parser import CsvParser

import re

year_regex = re.compile('[^\d]*(\d{4})[^\d]*')


class Book:
    def __init__(self, title, authors, publisher, published_year, categories):
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.published_year = published_year

        if self.published_year:
            self.published_year = self.get_year_regex(self.published_year)
        self.categories = categories

    def __str__(self):  # Title,description,authors,image,previewLink,publisher,publishedDate,infoLink,categories,ratingsCount
        return f"{self.title},{self.authors},{self.publisher},{self.published_year},{self.categories}"

    def sanitize(self):
        fields = [self.title, self.authors, self.published_year]

        if len(self.categories) == 1:
            if self.categories[0] == "":
                return False
        for i in range(len(fields)):
            if fields[i] == None or fields[i] == "":
                # print(f"Missing title, authors, categories or published year: {self.title}, {self.authors}, {self.categories}, {self.published_year}")
                return False
        return True

    @staticmethod
    def from_csv_line(line):
        parser = CsvParser()
        # print("Processing message: %s", line)
        parsed_line = parser.parse_csv(line)
        if len(parsed_line) != 5:
            return None

        return Book(*parsed_line)

    def get_year_regex(self, text):
        if text:
            result = year_regex.search(text)
            return int(result.group(1)) if result else None
        return None

    def parse_authors(self):
        authors = self.authors.replace('"', "").replace(
            "[", "").replace("]", "").replace("'", "").split(", ")
        return authors

    @staticmethod
    def expand_authors(book):
        authors = book.parse_authors()

        books = []
        for author in authors:
            books.append(Book(book.title, author, book.publisher,
                              book.published_year, book.categories))

        return books
