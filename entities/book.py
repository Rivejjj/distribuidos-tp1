
class Book:
    def __init__(self, title, authors, publisher, published_year, categories):
        self.title = title
        self.authors = authors
        self.publisher = publisher
        self.published_year = published_year
        self.categories = categories

    def __str__(self):  # Title,description,authors,image,previewLink,publisher,publishedDate,infoLink,categories,ratingsCount
        return f"{self.title}|{self.authors}|{self.publisher}|{self.published_year}|{self.categories}"
