from entities.query_message import EOF, QueryMessage


class EOFMessage(QueryMessage):
    def __init__(self, id: int, client_id: int):
        super().__init__(EOF, id, client_id)

    def serialize_data(self) -> str:
        return ""
