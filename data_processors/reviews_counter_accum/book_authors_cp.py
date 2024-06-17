import json
from data_checkpoints.data_checkpoint import DataCheckpoint
from reviews_counter import ReviewsCounter
from entities.book import Book


class BookAuthorsCheckpoint(DataCheckpoint):
    def __init__(self, counter: ReviewsCounter, save_path='.checkpoints/book_authors'):
        super().__init__(save_path)
        self.counter = counter
        self.load()

    def save(self, book: Book):
        """
        Guarda un autor en el archivo de checkpoint
        """
        self.checkpoint(json.dumps([book.title, book.authors]),
                        json.dumps(self.counter.books))

    def load(self):
        """
        Restaura el estado del filtro de reviews a partir del archivo de checkpoint
        """
        try:
            state = self.load_state()
            if state:
                self.counter.books = state

            for change in self.load_changes():
                title, authors = change

                book = Book(title, authors, None, None, None)
                self.counter.add_book(book)
        except FileNotFoundError:
            return
