import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from accumulator import Accumulator
from entities.book import Book


class AccumulatorCheckpoint(DataCheckpoint):
    def __init__(self, accumulator: Accumulator, save_path='.checkpoints/accumulator'):
        super().__init__(save_path)
        self.accumulator = accumulator
        self.load()

    def save(self, book: Book):
        """
        Guarda un autor en el archivo de checkpoint
        """
        authors = {authors: list(decade) for authors,
                   decade in self.accumulator.authors.items()}
        self.checkpoint(json.dumps([book.authors, book.published_year]),
                        json.dumps([authors, list(self.accumulator.completed_authors)]))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            state = self.load_state()
            if state:
                authors, completed_authors = state
                self.accumulator.authors = {author: set(decade) for author,
                                            decade in authors}
                self.accumulator.completed_authors = set(completed_authors)

            for change in self.load_changes():
                author, published_year = change

                book = Book(None, author, None, published_year, None)
                self.accumulator.add_book(book)
        except FileNotFoundError:
            return
