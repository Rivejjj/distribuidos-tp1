class query2:
    def __init__(self, authors):
        self.authors = {} #authors,decades

        
    def add(self, author, decade):
        if author not in self.authors:
            self.authors[author] = []
        self.authors[author].append(decade)

    def get_decade(self,year):
        pass

    def get_year_regex(self,text):
        matches = []
        if text == "":
            return None
        
        i = 0
        while i < len(text):
            if text[i].isdigit():
                digits = ""
                while i < len(text) and text[i].isdigit() and len(digits) < 4:
                    digits += text[i]
                    i += 1
                if len(digits) == 4:
                    matches.append(int(digits))
            else:
                i += 1

        return matches
            