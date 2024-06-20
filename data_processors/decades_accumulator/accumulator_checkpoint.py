import ujson as json
from data_checkpoints.data_checkpoint import DataCheckpoint
# from accumulator import Accumulator
from data_processors.decades_accumulator.accumulator import Accumulator
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
        self.checkpoint(json.dumps([book.authors, book.published_year, client_id]),
                        json.dumps([serialize_dict(self.accumulator.authors), serialize_dict(self.accumulator.completed_authors)]))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        # TODO: Que funcione teniendo en cuenta client id

        try:
            state = self.load_state()
            if state:
                authors, completed_authors = state
                self.accumulator.authors = deserialize_dict(authors)
                self.accumulator.completed_authors = deserialize_dict(
                    completed_authors)

            for change in self.load_changes():
                author, published_year, client_id = change

                book = Book(authors=author, published_year=published_year)
                self.accumulator.add_book(book, client_id)
        except FileNotFoundError:
            return
