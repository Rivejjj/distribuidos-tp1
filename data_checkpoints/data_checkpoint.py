from abc import ABC, abstractmethod
import json
import shutil
import os
DIRECTORY = 'data_checkpoints/.checkpoints'

MAX_LENGTH_BYTES = 8


class DataCheckpoint(ABC):
    def __init__(self, path, checkpoint_interval=10000):
        self.path = path
        self.checkpoint_interval = checkpoint_interval
        self.change_counter = {}

    def wal_path(self, client_id):
        return f"{self.path}/{client_id}/wal.txt"

    def cp_path(self, client_id):
        return f"{self.path}/{client_id}/checkpoint"

    def checkpoint(self, change_data, state_cb, client_id, add_length=True, add_new_line=True):
        """
        Almacena la informacion del cambio de estado en archivo
        Dependiendo de la configuracion de checkpoint, se guarda el estado entero cada n cambios
        La primera linea del archivo es el estado actual
        Las siguientes lineas son los cambios de estado
        """
        self.change_counter[client_id] = self.change_counter.get(
            client_id, 0) + 1
        self.save_change(change_data, client_id, add_length, add_new_line)
        if self.change_counter[client_id] % self.checkpoint_interval == 0:
            self.save_state(state_cb, client_id)
            self.change_counter[client_id] = 0

    def save_change(self, change_data, client_id, add_length=True, add_newline=True):
        os.makedirs(f"{self.path}/{client_id}", exist_ok=True)

        with open(self.wal_path(client_id), 'a') as f:
            if type(change_data) != str:
                change_data = json.dumps(change_data)
            line = []
            if add_length:
                line.append(str(len(change_data)))

            line.append(change_data)
            new_line = '\n'
            f.write(
                f"{','.join(line)}{new_line if add_newline else ''}")
            f.flush()

    def save_state(self, state_cb, client_id):
        os.makedirs(f"{self.path}/{client_id}", exist_ok=True)

        temp_path = f"{self.cp_path(client_id)}.tmp"

        with open(temp_path, 'w') as f:
            f.write(f"{json.dumps(state_cb())}")
            f.flush()

        os.replace(temp_path, f"{self.cp_path(client_id)}.txt")
        os.remove(self.wal_path(client_id))

    def load_state(self):
        """
        Devuelve el estado actual
        """
        clients = os.listdir(self.path)

        for client in clients:
            try:
                with open(f"{self.cp_path(client)}.txt") as f:
                    yield int(client), json.loads(f.readline().strip())
            except FileNotFoundError:
                pass

    def load_changes(self):
        """
        Devuelve los cambios hechos a partir del checkpoint creado
        """
        clients = os.listdir(self.path)

        for client in clients:
            try:
                with open(self.wal_path(client), 'r') as changes:
                    for line in changes:
                        line = line.strip().split(',', 1)

                        if len(line) != 2:
                            continue

                        length, data = line

                        # Truncar lineas corruptas

                        if int(length) == len(data):
                            yield int(client), json.loads(data)
            except FileNotFoundError:
                pass

    def delete_client(self, client_id):
        shutil.rmtree(f"{self.path}/{client_id}")
        self.change_counter.pop(client_id)

    @ abstractmethod
    def load(self):
        pass
