

from utils.to_str import to_str


class Review:
    def __init__(self, title, score, text):
        self.title = title
        self.score = score
        self.text = text

    def __str__(self):
        fields = [self.title, self.score, self.text]
        return to_str(fields)

    def sanitize(self):
        if not self.title or not self.score or not self.text:
            # print("Missing fields",self.title, self.score, self.text)
            return False
        return True