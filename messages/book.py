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

    def __str__(self):#Title,description,authors,image,previewLink,publisher,publishedDate,infoLink,categories,ratingsCount
        return f"{self.title},{self.description},{self.authors},{self.image},{self.preview_link},{self.publisher},{self.published_year},{self.info_link},{self.categories},{self.ratings_count}"

    def sanitize(self):
        if not self.title or not self.authors or not self.categories or not self.published_year:
            print("Missing title, authors, categories or published year", self.title, self.authors, self.categories, self.published_year)
            return False
        return True
    
