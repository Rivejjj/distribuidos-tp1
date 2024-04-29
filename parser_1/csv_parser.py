class CsvParser:
    def __init__(self):
        self.fields = []
    
    def parse_csv(self,line):
        between_quotes = False
        field = ""
        for char in line:
            if char == '"':
                between_quotes = not between_quotes
                
            if char == ',' and not between_quotes:
                self.fields.append(field)
                field = ""
            else:
                field += char
        self.fields.append(field)
        return self.fields

