

class Accumulator:
    def __init__(self):
        self.authors = {}  # author -> {decade -> count}
        self.completed_authors = set()

    def add_book(self, book):
        year = int(book.published_year)
        if year is None:
            return
        decade = self.__get_decade(year)
        self.__add_author(book.authors, decade)

        return self.check_valid_author(book.authors)

    def check_valid_author(self, author):
        if author in self.completed_authors:
            return False

        result = len(self.authors[author]) >= 10
        if result:
            self.completed_authors.add(author)
        return result

    def __add_author(self, author, decade):
        if author not in self.authors:
            self.authors[author] = set()
        self.authors[author].add(decade)
        # if len(self.authors[author]) >= 10:
        # print("author:", author, "->", self.authors[author])

    def __get_decade(self, year):
        return year // 10 * 10

    def clear(self):
        self.authors = {}
