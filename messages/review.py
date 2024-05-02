

from parser_1.csv_parser import CsvParser


class Review:
    def __init__(self, title, score, text):
        self.title = title
        self.score = score
        self.text = text

    def __str__(self):
        return f"{self.title},{self.score},{self.text}"

    def sanitize(self):
        if not self.title or not self.score or not self.text:
            # print("Missing fields",self.title, self.score, self.text)
            return False
        return True

    @staticmethod
    def from_csv_line(line):
        parser = CsvParser()
        # print("Processing message: %s", line)
        parsed_line = parser.parse_csv(line)
        if len(parsed_line) != 3:
            return None

        return Review(*parsed_line)
