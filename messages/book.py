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
                print(f"Missing title, authors, categories or published year: {self.title}, {self.authors}, {self.categories}, {self.published_year}")
                return False
        return True

    def get_year_regex(self, text):
        if text == "" or None:
            return None
        i = 0
        while i < len(text):
            if text[i].isdigit():
                digits = ""
                while i < len(text) and text[i].isdigit() and len(digits) < 4:
                    digits += text[i]
                    i += 1
                if len(digits) == 4:
                    return digits
            else:
                i += 1
        return None
