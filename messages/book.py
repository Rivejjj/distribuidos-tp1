class Book:
    def __init__(self, title, description, authors, image, preview_link, publisher, published_year, info_link, categories, ratings_count):
        self.title = title
        self.description = description
        self.authors = authors
        self.image = image
        self.preview_link = preview_link
        self.publisher = publisher
        self.published_year = published_year
        self.info_link = info_link
        self.categories = categories
        self.ratings_count = ratings_count

    def __str__(self):
        return f"{self.title},{self.description},{self.authors},{self.image},{self.preview_link},{self.publisher},{self.published_year},{self.info_link},{self.categories},{self.ratings_count}"

    def sanitize(self):
        self.published_year = self.get_year_regex(self.published_year)
        if not self.title or not self.authors or not self.categories or not self.published_year:
            print("Missing title, authors, categories or published year", self.title, self.authors, self.categories, self.published_year)
            return False
        return True
    
    def get_year_regex(self,text):
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