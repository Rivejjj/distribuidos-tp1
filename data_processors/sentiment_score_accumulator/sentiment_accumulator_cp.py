import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from sentiment_score_accumulator import SentimentScoreAccumulator


class SentimentAccumulatorCheckpoint(DataCheckpoint):
    def __init__(self, acc: SentimentScoreAccumulator, save_path='.checkpoints/sentiment_acc'):
        super().__init__(save_path)
        self.acc = acc
        self.load()

    def save(self, title: str, score: float, client_id: int):
        # TODO: Cambiar a que convierta self.titles a un diccionario donde los valores son listas

        self.checkpoint(json.dumps([title, score, client_id]),
                        json.dumps(self.acc.title_sentiment_score))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        # TODO: Que funcione teniendo en cuenta client id

        try:
            state = self.load_state()
            if state:
                self.acc.title_sentiment_score = state

            for change in self.load_changes():
                self.acc.add_sentiment_score(*change)
        except FileNotFoundError:
            return
