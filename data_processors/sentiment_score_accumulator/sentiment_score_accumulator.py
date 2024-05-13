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
        scores = [score[1]
                  for score in self.title_sentiment_score.values()]
        scores.sort()

        min_value = scores[int(len(scores) * 0.9)]

        return [(title, score[1]) for title, score in self.title_sentiment_score.items() if score[1] >= min_value]

    def clear(self):
        self.title_sentiment_score = {}
