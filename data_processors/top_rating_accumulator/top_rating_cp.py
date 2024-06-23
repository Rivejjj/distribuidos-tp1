import json
from data_checkpoints.data_checkpoint import DataCheckpoint
# from data_processors.top_rating_accumulator.top_rating_accumulator import TopRatingAccumulator
from utils.initialize import deserialize_dict, serialize_dict
from top_rating_accumulator import TopRatingAccumulator


class TopRatingCheckpoint(DataCheckpoint):
    def __init__(self, acc: TopRatingAccumulator, save_path='.checkpoints/top_rating'):
        super().__init__(save_path)
        self.acc = acc
        self.load()

    def save(self, title: str, score: float, client_id: int):
        """
        Guarda un autor en el archivo de checkpoint
        """
        self.checkpoint([title, score],
                        lambda: serialize_dict(self.acc.books[client_id]), client_id)

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            for client_id, state in self.load_state():
                self.acc.books[client_id] = deserialize_dict(state)

            for client_id, change in self.load_changes():
                self.acc.add_title(*change, client_id)

        except FileNotFoundError:
            return
