import math
from ..messages import Book
from ..messages import Review
class query2:
    def __init__(self):
        self.authors = {} #authors,decades

    def add(self, author, decade):
        if author not in self.authors:
            self.authors[author] = {}
        self.authors[author][decade] = self.authors[author].get(decade,0) + 1

    def add_book(self,book):
        year = self.get_year_regex(book.publishedDate)
        if year is None:
            return
        decade = self.get_decade(year[0])
        for author in book.authors:
            self.add(author,decade)

    def get_decade(self,year):
        return math.floor((year)%100/10)*10

    def get_year_regex(self,text):
        if text == "":
            return None
        i = 0
        while i < len(text):
            if text[i].isdigit():
                digits = ""
                while i < len(text) and text[i].isdigit() and len(digits) < 4:
                    digits += text[i]
                    i += 1
                if len(digits) == 4:
                    return int(digits)
            else:
                i += 1
        return None
        
