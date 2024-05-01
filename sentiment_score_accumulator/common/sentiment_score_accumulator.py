class SentimentScoreAccumulator:
    def __init__(self):
        self.title_sentiment_score = set()

    def add_sentiment_score(self, title, sentiment_score):
        print(f"[ACCUMULATOR]: {title}, {sentiment_score}")
        self.title_sentiment_score.add((title, sentiment_score))

    def calculate_90th_percentile(self):
        sentiment_scores = [score for _, score in self.title_sentiment_score]
        sentiment_scores.sort()
        return sentiment_scores[int(len(sentiment_scores) * 0.9)]

    def clear(self):
        self.title_sentiment_score = set()
