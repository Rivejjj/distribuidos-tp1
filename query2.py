class query2:
    def __init__(self, authors):
        self.authors = {} #authors,decades

        
    def add(self, author, decade):
        if author not in self.authors:
            self.authors[author] = []
        self.authors[author].append(decade)

    def get_decade(self,year):
        pass