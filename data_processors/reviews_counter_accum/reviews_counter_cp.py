import json
from data_checkpoints.data_checkpoint import DataCheckpoint
# from data_processors.reviews_counter_accum.reviews_counter import ReviewsCounter
from entities.review import Review
from reviews_counter import ReviewsCounter
from entities.book import Book
from utils.initialize import deserialize_dict, serialize_dict


class ReviewsCounterCheckpoint(DataCheckpoint):
    def __init__(self, counter: ReviewsCounter, save_path='.checkpoints/counter'):
        super().__init__(save_path)
        self.counter = counter
        self.load()

    def save(self, review: Review, client_id: int):
        """
        Guarda un autor en el archivo de checkpoint
        """
        self.checkpoint([review.title, review.score],
                        lambda: serialize_dict(self.counter.reviews[client_id]), client_id)

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            for client_id, state in self.load_state():
                self.counter.reviews[client_id] = deserialize_dict(
                    state, convert_to_set=False, convert_to_tuple=True)

            for client_id, change in self.load_changes():
                title, score = change

                review = Review(title, score)
                self.counter.add_review(review, client_id)

        except FileNotFoundError:
            return
