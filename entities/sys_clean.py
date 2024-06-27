from entities.query_message import SYSTEM_CLEAN, QueryMessage


class SystemCleanMessage(QueryMessage):
    def __init__(self, id: int, client_id: int):
        super().__init__(SYSTEM_CLEAN, id, client_id)

    def serialize_data(self) -> str:
        return ""
