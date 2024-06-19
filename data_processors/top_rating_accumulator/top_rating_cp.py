import json
from data_checkpoints.data_checkpoint import DataCheckpoint
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
        # TODO: Cambiar a que convierta self.titles a un diccionario donde los valores son listas

        self.checkpoint(json.dumps([title, score, client_id]),
                        json.dumps(self.acc.books))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        # TODO: Que funcione teniendo en cuenta client id

        try:
            state = self.load_state()
            if state:
                self.acc.books = state

            for change in self.load_changes():
                self.acc.add_title(*change)
        except FileNotFoundError:
            return
