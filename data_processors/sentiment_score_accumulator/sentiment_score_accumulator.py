from entities.query_message import QueryMessage


class SentimentScoreAccumulator:
    def __init__(self):
        self.title_sentiment_score = {}  # client -> title -> (count, total)

    def add_sentiment_score(self, title: str, sentiment_score: str, client_id: int):
        self.title_sentiment_score[client_id] = self.title_sentiment_score.get(
            client_id, {})
        count, total = self.title_sentiment_score[client_id].get(
            title, (0, 0))

        self.title_sentiment_score[client_id][title] = (
            count + 1, total + float(sentiment_score))

    def calculate_90th_percentile(self, client_id: int):
        title_scores = [(title, score[1] / score[0])
                        for title, score in self.title_sentiment_score[client_id].items()]
        title_scores.sort(key=lambda x: x[1])
        return title_scores[int(len(title_scores) * 0.9):]

    def clear(self, msg: QueryMessage):
        client_id = msg.get_client_id()
        self.title_sentiment_score.pop(client_id)
