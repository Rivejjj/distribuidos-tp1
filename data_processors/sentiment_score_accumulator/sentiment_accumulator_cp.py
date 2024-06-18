import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from sentiment_score_accumulator import SentimentScoreAccumulator


class SentimentAccumulatorCheckpoint(DataCheckpoint):
    def __init__(self, acc: SentimentScoreAccumulator, save_path='.checkpoints/sentiment_acc'):
        super().__init__(save_path)
        self.acc = acc
        self.load()

    def save(self, title, score):
        self.checkpoint(json.dumps([title, score]),
                        json.dumps(self.acc.title_sentiment_score))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            state = self.load_state()
            if state:
                self.acc.title_sentiment_score = state

            for change in self.load_changes():
                self.acc.add_sentiment_score(*change)
        except FileNotFoundError:
            return
