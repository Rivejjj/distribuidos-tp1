import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from entities.review import Review
from reviews_counter import ReviewsCounter
from entities.book import Book


class SentTitlesCheckpoint(DataCheckpoint):
    def __init__(self, save_path='.checkpoints/counter'):
        super().__init__(save_path)
        self.titles = {}
        self.load()

    def save(self, title: str, client_id: int):
        self.titles[client_id] = self.titles.get(client_id, set())
        self.titles[client_id].add(title)

        # TODO: Cambiar a que convierta self.titles a un diccionario donde los valores son listas
        self.checkpoint(json.dumps([title, client_id]),
                        json.dumps(list(self.titles)))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """

        # TODO: Que funcione teniendo en cuenta client id
        try:
            state = self.load_state()
            if state:
                self.titles = set(state)

            for change in self.load_changes():
                self.save(change)
        except FileNotFoundError:
            return

    def not_sent(self, title: str, client_id: int):
        self.titles[client_id] = self.titles.get(client_id, set())
        return title not in self.titles[client_id]
