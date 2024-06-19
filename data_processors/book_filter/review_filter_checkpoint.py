import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from review_filter import ReviewFilter


class ReviewFilterCheckpoint(DataCheckpoint):
    def __init__(self, review_filter: ReviewFilter, save_path='data_checkpoints/.checkpoints/review_filter'):
        super().__init__(save_path)
        self.review_filter = review_filter
        self.load()

    def save(self, new_book_title: str, client_id: int):
        """
        Guarda el titulo del libro en el archivo de checkpoint
        Asume que el titulo del libro ya fue guardado en el filtro
        """
        self.checkpoint(json.dumps([new_book_title, client_id]),
                        json.dumps(list(self.review_filter.titles)))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            state = self.load_state()
            if state:
                self.review_filter.titles = set(state)
            for change, client_id in self.load_changes():
                self.review_filter.add_title(change, client_id)
        except FileNotFoundError:
            return
