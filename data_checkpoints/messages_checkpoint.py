import json
import os
from data_checkpoints.data_checkpoint import DataCheckpoint
from entities.query_message import QueryMessage

MSG_SENT_MARK = '+'


class MessagesCheckpoint(DataCheckpoint):
    def __init__(self, save_path):
        super().__init__(save_path)
        # ID del mensaje como clave. El valor es un booleano que indica si el mensaje fue enviado
        self.processed_messages = {}
        self.pending_message = {}
        self.load()

    def save(self, msg: QueryMessage):
        id = msg.get_id()
        client_id = msg.get_client_id()
        if self.pending_message:
            self.save_change('\n', client_id, False, True)

        self.processed_messages[client_id] = self.processed_messages.get(
            client_id, {})
        self.processed_messages[client_id][id] = False
        self.pending_message[client_id] = self.pending_message.get(
            client_id, False)
        self.checkpoint(id,
                        lambda: self.get_messages(client_id), client_id, add_new_line=False)

        self.change_counter[client_id] -= 1

    def get_messages(self, client_id: int):
        unsent = []
        sent = []
        for msg, is_sent in self.processed_messages.get(client_id, {}).items():
            if is_sent:
                sent.append(msg)
            else:
                unsent.append(msg)

        return [sent, unsent]

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            for client_id, state in self.load_state():
                print(client_id, state)
                sent, unsent = state
                self.processed_messages[client_id] = {
                    msg: True for msg in sent}

                for msg in unsent:
                    self.processed_messages[client_id][msg] = False

                self.pending_message[client_id] = False

                if len(unsent) > 0:
                    self.pending_message[client_id] = True

            for client_id, msg, is_sent in self.load_changes():
                print(client_id, msg, is_sent)

                self.processed_messages[client_id] = self.processed_messages.get(
                    client_id, {})
                self.processed_messages[client_id][msg] = is_sent
        except FileNotFoundError:
            return

    def mark_msg_as_sent(self, msg: QueryMessage):
        id = msg.get_id()
        client_id = msg.get_client_id()
        self.processed_messages[client_id][id] = True
        self.pending_message[client_id] = False

        self.checkpoint(MSG_SENT_MARK,
                        lambda: self.get_messages(client_id), client_id, add_length=False)

    def load_changes(self):
        """
        Devuelve los cambios hechos a partir del checkpoint creado
        """
        clients = os.listdir(self.path)

        for client in clients:
            with open(self.wal_path(client), 'r') as changes:
                for line in changes:
                    line = line.strip().split(',', 1)

                    if len(line) != 2:
                        continue

                    length, data = line

                    last_char = data[-1]

                    correct_last_char = last_char == MSG_SENT_MARK

                    if correct_last_char:
                        data = data[:len(data)-1]

                    if int(length) == len(data):
                        yield int(client), json.loads(data), correct_last_char

    def is_sent_msg(self, msg: QueryMessage):
        id = msg.get_id()
        client_id = msg.get_client_id()
        messages = self.processed_messages.get(client_id, {})

        return id in messages and messages[id]

    def is_processed_msg(self, msg: QueryMessage):
        id = msg.get_id()
        client_id = msg.get_client_id()

        messages = self.processed_messages.get(client_id, {})
        return id in messages and not messages[id]
