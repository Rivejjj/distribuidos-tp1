import json
from data_checkpoints.data_checkpoint import DataCheckpoint
# from reviews_counter import ReviewsCounter
from data_processors.reviews_counter_accum.reviews_counter import ReviewsCounter
from entities.book import Book
from utils.initialize import deserialize_dict


class BookAuthorsCheckpoint(DataCheckpoint):
    def __init__(self, counter: ReviewsCounter, save_path='.checkpoints/book_authors'):
        super().__init__(save_path)
        self.counter = counter
        self.load()

    def save(self, book: Book, client_id: int):
        """
        Guarda un autor en el archivo de checkpoint
        """
        self.checkpoint([book.title, book.authors, client_id],
                        lambda: self.counter.books)

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        # TODO: Que funcione teniendo en cuenta client id

        try:
            state = self.load_state()
            if state:
                self.counter.books = deserialize_dict(state)

            for change in self.load_changes():
                title, authors, client_id = change

                book = Book(title, authors)
                self.counter.add_book(book, client_id)
        except FileNotFoundError:
            return
