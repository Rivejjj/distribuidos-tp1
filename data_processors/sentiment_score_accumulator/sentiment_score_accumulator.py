class SentimentScoreAccumulator:
    def __init__(self):
        self.title_sentiment_score = {}  # title -> (count, average)

    def add_sentiment_score(self, title, sentiment_score):
        if title not in self.title_sentiment_score:
            self.title_sentiment_score[title] = (1, float(sentiment_score))
        else:
            count, average = self.title_sentiment_score[title]
            new_avg = float(
                average) + ((float(sentiment_score) - float(average)) / (count + 1))
            self.title_sentiment_score[title] = (count + 1, new_avg)

    def calculate_90th_percentile(self):
        title_scores = [(title, score[1])
                        for title, score in self.title_sentiment_score.items()]
        title_scores.sort(key=lambda x: x[1])
        return title_scores[int(len(title_scores) * 0.9):]

    def clear(self):
        self.title_sentiment_score = {}