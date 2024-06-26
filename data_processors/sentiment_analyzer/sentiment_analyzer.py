from textblob import TextBlob


class SentimentAnalyzer:
    def __init__(self):
        pass

    def analyze(self, text):
        if isinstance(text, str):
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
            return sentiment
        else:
            return None
