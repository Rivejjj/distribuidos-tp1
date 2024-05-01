
class ReviewsCounter:
    def __init__(self,min_reviews):
        self.min_reviews = min_reviews
        self.books = {} # title -> author
        self.reviews = {} # title -> (review_count,average_rating)

    def add_book(self,book):
        self.books[book.title] = book.authors

    def add_review(self,review):
        if review.title in self.reviews:
            count, average = self.reviews[review.title]
            review_score = review.score
            new_avg = float(average) + (float(review_score) - float(average)) / (count + 1)
            self.reviews[review.title] = (count + 1, new_avg)
        else:
            score = review.score
            self.reviews[review.title] = (1, score)
        
        if int(self.reviews[review.title][0]) > self.min_reviews:
            average = self.reviews[review.title][1]
            author = self.books[review.title]
            return author, review.title, average
        return None, None, None

