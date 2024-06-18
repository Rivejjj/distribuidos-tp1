
from entities.book import Book
from entities.review import Review


class ReviewsCounter:
    def __init__(self, min_reviews=500):
        self.min_reviews = min_reviews
        self.books = {}  # title -> author
        self.reviews = {}  # title -> (review_count,average_rating)

    def add_book(self, book: Book):
        self.books[book.title] = book.authors

    def add_review(self, review: Review):
        title = review.title
        score = float(review.score)

        count, total = self.reviews.get(title, (0, 0))
        count += 1
        total += score
        self.reviews[title] = (count, total)

        return self.get_review(review)

    def review_more_than_min(self, review: Review):
        title = review.title

        count, _ = self.reviews.get(title, (0, 0))

        return count >= self.min_reviews

    def get_review(self, review: Review):
        title = review.title

        count, total = self.reviews.get(title, (0, 0))

        average = total / count
        author = self.books[title]
        return author, title, average

    def clear(self):
        self.books = {}
        self.reviews = {}
