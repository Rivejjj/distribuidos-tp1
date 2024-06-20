import ujson as json
from data_checkpoints.data_checkpoint import DataCheckpoint
from utils.initialize import deserialize_dict, serialize_dict


class SentTitlesCheckpoint(DataCheckpoint):
    def __init__(self, save_path='.checkpoints/counter'):
        super().__init__(save_path)
        self.titles = {}
        self.load()

    def save(self, title: str, client_id: int):
        self.titles[client_id] = self.titles.get(client_id, set())
        self.titles[client_id].add(title)

        self.checkpoint(json.dumps([title, client_id]),
                        json.dumps(serialize_dict(self.titles)))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            state = self.load_state()
            if state:
                self.titles = deserialize_dict(state)

            for change in self.load_changes():
                self.save(*change)
        except FileNotFoundError:
            return

    def not_sent(self, title: str, client_id: int):
        self.titles[client_id] = self.titles.get(client_id, set())
        return title not in self.titles[client_id]
