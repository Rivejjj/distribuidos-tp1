
class Accumulator:
    def __init__(self):
        self.authors = {} # author -> {decade -> count}
        self.reviews = {} # title -> (review_count,average_rating)

    def add_book(self,book):
        year = self.__get_year_regex(book.published_year)
        if year is None:
            return
        decade = self.__get_decade(year)
        for author in book.authors.split(","):
            self.__add_author(author,decade)

    def add_review(self,review):
        if review.title in self.reviews:
            count, average = self.reviews[review.title]
            new_avg = average + (review.score - average) / (count + 1)
            self.reviews[review.title] = (count + 1, new_avg)
        else:
            self.reviews[review.title] = (1, review.score)


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
        
