import ujson as json
from data_checkpoints.data_checkpoint import DataCheckpoint
from data_processors.sentiment_score_accumulator.sentiment_score_accumulator import SentimentScoreAccumulator
from utils.initialize import deserialize_dict, serialize_dict
# from sentiment_score_accumulator import SentimentScoreAccumulator


class SentimentAccumulatorCheckpoint(DataCheckpoint):
    def __init__(self, acc: SentimentScoreAccumulator, save_path='.checkpoints/sentiment_acc'):
        super().__init__(save_path)
        self.acc = acc
        self.load()

    def save(self, title: str, score: float, client_id: int):
        self.checkpoint(json.dumps([title, score, client_id]),
                        json.dumps(serialize_dict(self.acc.title_sentiment_score)))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """

        try:
            state = self.load_state()
            if state:
                self.acc.title_sentiment_score = deserialize_dict(
                    state, convert_to_set=False, convert_to_tuple=True)

            for change in self.load_changes():
                self.acc.add_sentiment_score(*change)
        except FileNotFoundError:
            return
