
class Accumulator:
    def __init__(self):
        self.authors = {} 

    def add_book(self,book):
        year = self.__get_year_regex(book.published_year)
        if year is None:
            return
        decade = self.__get_decade(year)
        for author in book.authors.split(","):
            self.__add_author(author,decade)


    def __add_author(self, author, decade):
        if author not in self.authors:
            self.authors[author] = {}
        self.authors[author][decade] = self.authors[author].get(decade,0) + 1
        print(self.authors)


    def __get_decade(self,year):
        return (year // 10) * 10


    def __get_year_regex(self,year):
        text = str(year)
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
        
