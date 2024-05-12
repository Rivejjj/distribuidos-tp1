
import re

year_regex = re.compile('[^\d]*(\d{4})[^\d]*')


class Book:
    def __init__(self, title, authors, publisher, published_year, categories):
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.published_year = published_year
        self.categories = categories

    def __str__(self):  # Title,description,authors,image,previewLink,publisher,publishedDate,infoLink,categories,ratingsCount
        return f"{self.title},{self.authors},{self.publisher},{self.published_year},{self.categories}"

    def sanitize(self):
        self.published_year = self.get_year_regex(self.published_year)
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
    def from_query_message(line):
        parsed_line = line.split(',')
        if len(parsed_line) != 5:
            return None

        return Book(*parsed_line)

    def get_year_regex(self, text):
        if text:
            result = year_regex.search(text)
            return int(result.group(1)) if result else None
        return None
