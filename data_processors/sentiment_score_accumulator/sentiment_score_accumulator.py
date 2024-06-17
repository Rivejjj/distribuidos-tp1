class SentimentScoreAccumulator:
    def __init__(self):
        self.title_sentiment_score = {}  # title -> (count, total)

    def add_sentiment_score(self, title, sentiment_score):
        count, total = self.title_sentiment_score.get(
            title, (0, 0))

        self.title_sentiment_score[title] = (
            count + 1, total + float(sentiment_score))

    def calculate_90th_percentile(self):
        title_scores = [(title, score[1] / score[0])
                        for title, score in self.title_sentiment_score.items()]
        title_scores.sort(key=lambda x: x[1])
        return title_scores[int(len(title_scores) * 0.9):]

    def clear(self):
        self.title_sentiment_score = {}
