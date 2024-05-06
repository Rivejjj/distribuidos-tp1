class SentimentScoreAccumulator:
    def __init__(self,amount):
        self.amount = amount
        self.title_sentiment_score = {} # title -> (count, average)

    def add_sentiment_score(self, title, sentiment_score):
        print(f"[ACCUMULATOR]: {title}, {sentiment_score}")
        if title not in self.title_sentiment_score:
            self.title_sentiment_score[title] = (1,sentiment_score)
        else:
            count, average = self.title_sentiment_score[title]
            new_avg = float(average) +( (float(sentiment_score) - float(average)) / (count + 1) )
            self.title_sentiment_score[title] = (count + 1, new_avg)

    def calculate_90th_percentile(self):
        print("[ACCUMULATOR]: Calculating 90th percentile")
        title_scores = [(title, score[1]) for title, score in self.title_sentiment_score.items()]
        print("title scores: ",title_scores)
        title_scores.sort(key=lambda x: x[1])
        print("title scores sorted: ",title_scores)
        print("title scores length: ",len(title_scores))
        print("title scores 90th percentile: ",title_scores[int(len(title_scores) * 0.9):])
        return title_scores[int(len(title_scores) * 0.9):]
    
    

    def clear(self):
        self.title_sentiment_score = {}

    