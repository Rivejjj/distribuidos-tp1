import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from accumulator import Accumulator
# from data_processors.decades_accumulator.accumulator import Accumulator
from entities.book import Book
from utils.initialize import deserialize_dict, serialize_dict


class AccumulatorCheckpoint(DataCheckpoint):
    def __init__(self, accumulator: Accumulator, save_path='.checkpoints/accumulator'):
        super().__init__(save_path)
        self.accumulator = accumulator
        self.load()

    def save(self, book: Book, client_id: int):
        """
        Guarda un autor en el archivo de checkpoint
        """
        self.checkpoint([book.authors, book.published_year],
                        lambda: [serialize_dict(self.accumulator.authors[client_id]), serialize_dict(self.accumulator.completed_authors[client_id])], client_id)

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """

        try:
            for client_id, state in self.load_state():
                authors, completed_authors = state
                self.accumulator.authors[client_id] = deserialize_dict(authors)
                self.accumulator.completed_authors[client_id] = deserialize_dict(
                    completed_authors)

            for client_id, change in self.load_changes():
                author, published_year = change
                book = Book(authors=author, published_year=published_year)
                self.accumulator.add_book(book, client_id)
        except FileNotFoundError:
            return
