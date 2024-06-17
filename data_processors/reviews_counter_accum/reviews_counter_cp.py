import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from entities.review import Review
from reviews_counter import ReviewsCounter
from entities.book import Book


class ReviewsCounterCheckpoint(DataCheckpoint):
    def __init__(self, counter: ReviewsCounter, save_path='.checkpoints/counter'):
        super().__init__(save_path)
        self.counter = counter
        self.load()

    def save(self, review: Review):
        """
        Guarda un autor en el archivo de checkpoint
        """
        self.checkpoint(json.dumps([review.title, review.score]),
                        json.dumps(self.counter.reviews))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            state = self.load_state()
            if state:
                self.counter.reviews = state

            for change in self.load_changes():
                title, score = change

                review = Review(title, score, None)
                self.counter.add_review(review)
        except FileNotFoundError:
            return