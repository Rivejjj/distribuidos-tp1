from entities.query_message import CLIENT_DC, QueryMessage


class ClientDCMessage(QueryMessage):
    def __init__(self, id: int, client_id: int):
        super().__init__(CLIENT_DC, id, client_id)

    def serialize_data(self) -> str:
        return ""
