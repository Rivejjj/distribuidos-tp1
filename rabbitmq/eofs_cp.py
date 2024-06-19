import json
from data_checkpoints.data_checkpoint import DataCheckpoint


class ReceivedEOF(DataCheckpoint):
    def __init__(self, eof_count: int, save_path='.checkpoints/eof'):
        super().__init__(save_path)
        self.eofs = {}
        self.eof_count = eof_count
        self.load()

    def save(self, client_id: int):
        self.add_eof(client_id)
        self.checkpoint(json.dumps([client_id]),
                        json.dumps(self.eofs))

    def add_eof(self, client_id: int):
        self.eofs[client_id] = self.eofs.get(client_id, 0) + 1

    def eof_reached(self, client_id: int) -> bool:
        return self.eofs[client_id] >= self.eof_count

    def reset_eof(self, client_id: int):
        self.eofs.pop(client_id)

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """

        try:
            state = self.load_state()
            if state:
                self.eofs = state

            for change in self.load_changes():
                self.add_eof(change)
        except FileNotFoundError:
            return
