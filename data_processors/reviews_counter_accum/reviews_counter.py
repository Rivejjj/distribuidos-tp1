
from entities.book import Book
from entities.query_message import QueryMessage
from entities.review import Review


class ReviewsCounter:
    def __init__(self, min_reviews=500):
        self.min_reviews = min_reviews
        self.books = {}  # client -> title -> author
        self.reviews = {}  # client -> title -> (review_count,average_rating)

    def add_book(self, book: Book, client_id: int):
        self.books[client_id] = self.books.get(client_id, {})
        self.books[client_id][book.title] = book.authors

    def add_review(self, review: Review, client_id: int):
        title = review.title
        score = float(review.score)

        self.reviews[client_id] = self.reviews.get(client_id, {})
        count, total = self.reviews[client_id].get(title, (0, 0))
        count += 1
        total += score
        self.reviews[client_id][title] = (count, total)

        return self.get_review(review, client_id)

    def review_more_than_min(self, review: Review, client_id: int):
        title = review.title

        self.reviews[client_id] = self.reviews.get(client_id, {})

        count, _ = self.reviews[client_id].get(title, (0, 0))

        return count >= self.min_reviews

    def get_review(self, review: Review, client_id: int):
        title = review.title

        self.reviews[client_id] = self.reviews.get(client_id, {})
        count, total = self.reviews[client_id].get(title, (0, 0))

        average = total / count

        self.books[client_id] = self.books.get(client_id, {})
        self.books[client_id][title] = self.books[client_id].get(title, None)
        author = self.books[client_id][title]
        return author, title, average

    def clear(self, msg: QueryMessage):
        client_id = msg.get_client_id()

        if client_id in self.books:
            self.books.pop(client_id)

        if client_id in self.reviews:
            self.reviews.pop(client_id)
