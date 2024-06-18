import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from entities.review import Review
from reviews_counter import ReviewsCounter
from entities.book import Book


class SentTitlesCheckpoint(DataCheckpoint):
    def __init__(self, save_path='.checkpoints/counter'):
        super().__init__(save_path)
        self.titles = set()
        self.load()

    def save(self, title: str):
        self.titles.add(title)
        self.checkpoint(json.dumps(title),
                        json.dumps(list(self.titles)))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            state = self.load_state()
            if state:
                self.titles = set(state)

            for change in self.load_changes():
                self.save(change)
        except FileNotFoundError:
            return

    def not_sent(self, title: str):
        return title not in self.titles
