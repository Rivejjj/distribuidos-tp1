import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from accumulator import Accumulator


class AccumulatorCheckpoint(DataCheckpoint):
    def __init__(self, accumulator: Accumulator, save_path='.checkpoints/accumulator'):
        super().__init__(save_path)
        self.accumulator = accumulator
        self.load()

    def save(self, author: str):
        """
        Guarda un autor en el archivo de checkpoint
        """
        self.checkpoint(json.dumps(author),
                        json.dumps([self.accumulator.authors, list(self.accumulator.completed_authors)]))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            state = self.load_state()
            if state:
                self.review_filter.titles = set(state)
            for change in self.load_changes():
                self.review_filter.add_title(change)
        except FileNotFoundError:
            return
