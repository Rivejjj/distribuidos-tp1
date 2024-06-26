import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from entities.query_message import QueryMessage
from utils.initialize import deserialize_dict, serialize_dict


class SentTitlesCheckpoint(DataCheckpoint):
    def __init__(self, save_path='.checkpoints/sent_titles'):
        super().__init__(save_path)
        self.titles = {}
        self.load()

    def save(self, title: str, client_id: int):
        self.titles[client_id] = self.titles.get(client_id, set())
        self.titles[client_id].add(title)

        self.checkpoint([title],
                        lambda: serialize_dict(self.titles[client_id]), client_id)

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:

            for client_id, state in self.load_state():
                self.titles[client_id] = deserialize_dict(state)

            for client_id, change in self.load_changes():
                self.save(*change, client_id)
        except FileNotFoundError:
            return

    def not_sent(self, title: str, client_id: int):
        self.titles[client_id] = self.titles.get(client_id, set())
        return title not in self.titles[client_id]

    def delete_client(self, msg: QueryMessage):
        client_id = msg.get_client_id()
        if client_id in self.titles:
            self.titles.pop(client_id)
        return super().delete_client(msg)
