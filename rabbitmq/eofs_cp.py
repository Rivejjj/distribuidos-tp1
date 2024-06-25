import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from entities.query_message import QueryMessage


class ReceivedEOF(DataCheckpoint):
    def __init__(self, eof_count: int, save_path='.checkpoints/eof', save_to_file=True):
        super().__init__(save_path)
        self.eofs = {}
        self.eof_count = eof_count
        self.save_to_file = save_to_file
        self.load()

    def save(self, client_id: int):
        self.add_eof(client_id)
        if self.save_to_file:
            self.checkpoint([self.eofs[client_id]],
                            lambda: self.eofs[client_id], client_id)

    def add_eof(self, client_id: int):
        self.eofs[client_id] = self.eofs.get(client_id, 0) + 1

    def eof_reached(self, client_id: int) -> bool:
        return self.eofs[client_id] >= self.eof_count

    def clear(self, msg: QueryMessage):
        client_id = msg.get_client_id()
        if client_id in self.eofs:
            self.eofs.pop(client_id)
        super().delete_client(msg)

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """

        try:
            for client_id, state in self.load_state():
                self.eofs[client_id] = state
            for client_id, change in self.load_changes():
                self.eofs[client_id] = change[0]
        except FileNotFoundError:
            return
