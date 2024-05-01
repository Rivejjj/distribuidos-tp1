class SentimentScoreAccumulator:
    def __init__(self):
        self.title_sentiment_score = set()

    def add_sentiment_score(self, title, sentiment_score):
        print(f"[ACCUMULATOR]: {title}, {sentiment_score}")
        self.title_sentiment_score.add((title, sentiment_score))

    def calculate_90th_percentile(self):
        print("[ACCUMULATOR]: Calculating 90th percentile")
        title_scores = list(self.title_sentiment_score)
        title_scores.sort(key=lambda x: x[1])
        return title_scores[int(len(title_scores) * 0.9):]

    def clear(self):
        self.title_sentiment_score = set()
