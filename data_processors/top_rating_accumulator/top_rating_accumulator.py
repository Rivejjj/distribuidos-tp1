AVG_RATING_POSITION = 1
TITLE_POSITON = 0


class TopRatingAccumulator:
    def __init__(self, top=10):
        self.top = top
        self.books = {}  # title -> avg_rating

    def add_title(self, title, avg_rating):
        self.books[title] = float(avg_rating)

    def get_top(self):
        top_books = []
        sorted_dict = sorted(self.books.items(),
                             key=lambda x: x[1], reverse=True)
        for i in range(min(self.top, len(sorted_dict))):
            top_books.append(sorted_dict[i])

        return top_books

    def clear(self):
        self.books = {}
