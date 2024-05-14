import logging

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
        scores = [score[1] for score in self.title_sentiment_score.values()]
        scores.sort()
        percentile = self.calculate_percentile(scores, 90)

        logging.info(f"90th percentile: {percentile}")

        return [(title, score[1]) for title, score in self.title_sentiment_score.items() if score[1] >= percentile]
    
    def calculate_percentile(self,data, percentile):
        index = (len(data) - 1) * (percentile / 100)  
        floor = int(index)  
        ceiling = floor + 1  
        if ceiling >= len(data):  
            return data[index]
        d0 = data[floor] * (ceiling - index)
        d1 = data[ceiling] * (index - floor)
        return d0 + d1

    def clear(self):
        self.title_sentiment_score = {}
