
class ReviewsCounter:
    def __init__(self, amount = 0):
        self.amount = amount
        self.books = {} # title -> Book
        self.reviews = {} # title -> (review_count,average_rating)

    def add_book(self,book):
        self.books[book.title] = book

    def add_review(self,review):
        if review.title in self.reviews:
            count, average = self.reviews[review.title]
            new_avg = average + (review.score - average) / (count + 1)
            self.reviews[review.title] = (count + 1, new_avg)
        else:
            self.reviews[review.title] = (1, review.score)

