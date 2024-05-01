

from messages.review import Review


class ReviewFilter:
    def __init__(self):
        self.titles = set()

    def add_title(self, title: str):
        self.titles.add(title)

    def filter(self, review: Review) -> bool:
        return review.title in self.titles

    def clear(self):
        self.titles = set()
