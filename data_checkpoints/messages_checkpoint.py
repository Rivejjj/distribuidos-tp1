import ujson as json
from data_checkpoints.data_checkpoint import DataCheckpoint
from entities.query_message import QueryMessage

MSG_SENT_MARK = '+'


class MessagesCheckpoint(DataCheckpoint):
    def __init__(self, save_path):
        super().__init__(save_path)
        # ID del mensaje como clave. El valor es un booleano que indica si el mensaje fue enviado
        self.processed_messages = {}
        self.pending_message = False
        self.load()

    def save(self, msg: QueryMessage):
        id = msg.get_id()
        if self.pending_message:
            raise Exception('Hay un mensaje sin enviar')
        self.processed_messages[id] = False
        self.pending_message = True
        self.checkpoint(json.dumps(id), json.dumps(
            self.get_messages()), add_new_line=False)

        self.change_counter -= 1

    def get_messages(self):
        unsent = []
        sent = []
        for msg, is_sent in self.processed_messages.items():
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
            state = self.load_state()
            if state:
                sent, unsent = state
                self.processed_messages = {msg: True for msg in sent}
                for msg in unsent:
                    self.processed_messages[msg] = False

            for msg, is_sent in self.load_changes():
                self.processed_messages[msg] = is_sent
        except FileNotFoundError:
            return

    def mark_msg_as_sent(self, msg: QueryMessage):
        id = msg.get_id()
        if id not in self.processed_messages:
            raise Exception("Mensaje no fue guardado")
        self.processed_messages[id] = True
        self.pending_message = False

        self.checkpoint(MSG_SENT_MARK, json.dumps(
            self.get_messages()), add_length=False)

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

                last_char = data[-1]

                correct_last_char = last_char == MSG_SENT_MARK

                if correct_last_char:
                    data = data[:len(data)-1]

                if int(length) == len(data):
                    yield json.loads(data), correct_last_char

    def is_sent_msg(self, msg: QueryMessage):
        return msg.get_id() in self.processed_messages and self.processed_messages[msg.get_id()]

    def is_processed_msg(self, msg: QueryMessage):
        return msg.get_id() in self.processed_messages and not self.processed_messages[msg.get_id()]
