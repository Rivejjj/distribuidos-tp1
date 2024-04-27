from textblob import TextBlob

class SentimentAnalizer:
    def __init__(self):
        pass

    def analyze(self, text):
        if isinstance(text, list):
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
            return sentiment
        else: 
            return None