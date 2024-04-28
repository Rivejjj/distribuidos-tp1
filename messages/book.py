

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

    def has_empty_fields(self):
        return not all([self.title, self.description, self.authors, self.image, self.preview_link, self.publisher, self.published_year, self.info_link, self.categories, self.ratings_count])
