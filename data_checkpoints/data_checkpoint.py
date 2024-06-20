from abc import ABC, abstractmethod
import ujson as json
import os
DIRECTORY = 'data_checkpoints/.checkpoints'

MAX_LENGTH_BYTES = 8


class DataCheckpoint(ABC):
    def __init__(self, path, checkpoint_interval=100000):
        os.makedirs(path, exist_ok=True)
        self.wal_path = f"{path}/wal.txt"
        self.cp_path = f"{path}/checkpoint"
        self.checkpoint_interval = checkpoint_interval
        self.change_counter = 0

    def checkpoint(self, change_data, cur_state, add_length=True, add_new_line=True):
        """
        Almacena la informacion del cambio de estado en archivo
        Dependiendo de la configuracion de checkpoint, se guarda el estado entero cada n cambios
        La primera linea del archivo es el estado actual
        Las siguientes lineas son los cambios de estado
        """
        self.change_counter += 1
        self.save_change(change_data, add_length, add_new_line)
        if self.change_counter % self.checkpoint_interval == 0:
            self.save_state(cur_state)
            self.change_counter = 0

    def save_change(self, change_data, add_length=True, add_newline=True):
        with open(self.wal_path, 'a') as f:
            line = []
            if add_length:
                line.append(str(len(change_data)))

            line.append(change_data)
            new_line = '\n'
            f.write(
                f"{','.join(line)}{new_line if add_newline else ''}")

    def save_state(self, state):
        temp_path = f"{self.cp_path}.tmp"

        with open(temp_path, 'w') as f:
            f.write(f"{state}")

        os.replace(temp_path, f"{self.cp_path}.txt")
        os.remove(self.wal_path)

    def load_state(self):
        """
        Devuelve el estado actual
        """
        try:
            with open(f"{self.cp_path}.txt", 'r') as state:
                return json.loads(state.readline().strip())
        except FileNotFoundError:
            return None

    def load_changes(self):
        """
        Devuelve los cambios hechos a partir del checkpoint creado
        """
        with open(self.wal_path, 'r') as changes:
            for line in changes:
                line = line.strip().split(',', 1)

                if len(line) != 2:
                    continue

                length, data = line

                if int(length) == len(data):
                    yield json.loads(data)

    @abstractmethod
    def load(self):
        pass
