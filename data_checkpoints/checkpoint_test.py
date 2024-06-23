import os
import unittest
import shutil

from data_checkpoints.messages_checkpoint import MessagesCheckpoint
from data_processors.book_filter.review_filter_checkpoint import ReviewFilterCheckpoint
from data_processors.book_filter.review_filter import ReviewFilter
from data_processors.decades_accumulator.accumulator import Accumulator
from data_processors.decades_accumulator.accumulator_checkpoint import AccumulatorCheckpoint
from data_processors.reviews_counter_accum.book_authors_cp import BookAuthorsCheckpoint
from data_processors.reviews_counter_accum.reviews_counter import ReviewsCounter
from data_processors.reviews_counter_accum.reviews_counter_cp import ReviewsCounterCheckpoint
from data_processors.reviews_counter_accum.sent_titles_cp import SentTitlesCheckpoint
from data_processors.sentiment_score_accumulator.sentiment_accumulator_cp import SentimentAccumulatorCheckpoint
from data_processors.sentiment_score_accumulator.sentiment_score_accumulator import SentimentScoreAccumulator
from data_processors.top_rating_accumulator.top_rating_accumulator import TopRatingAccumulator
from data_processors.top_rating_accumulator.top_rating_cp import TopRatingCheckpoint
from entities.book import Book
from entities.book_msg import BookMessage
from entities.review import Review
from gateway.client_parser import parse_book_from_client

CLIENTS = 3
INTERVAL = 100


def new_filter(path='data_checkpoints/.checkpoints/tests'):
    review_filter = ReviewFilter()
    cp = ReviewFilterCheckpoint(
        review_filter, path)

    cp.checkpoint_interval = INTERVAL
    return review_filter, cp


def new_acc(path='data_checkpoints/.checkpoints/tests'):
    acc = Accumulator()
    cp = AccumulatorCheckpoint(acc, path)

    cp.checkpoint_interval = INTERVAL
    return acc, cp


def new_reviews_counter(path='data_checkpoints/.checkpoints/tests'):
    counter = ReviewsCounter()
    b_cp = BookAuthorsCheckpoint(counter, f"{path}/b_authors")
    r_cp = ReviewsCounterCheckpoint(counter, f"{path}/f_authors")
    sent_titles_cp = SentTitlesCheckpoint(f"{path}/sent_titles_authors")

    r_cp.checkpoint_interval = INTERVAL
    b_cp.checkpoint_interval = INTERVAL
    sent_titles_cp.checkpoint_interval = INTERVAL

    return counter, r_cp, b_cp, sent_titles_cp


def new_sentiment_score_acc(path='data_checkpoints/.checkpoints/tests'):
    acc = SentimentScoreAccumulator()
    cp = SentimentAccumulatorCheckpoint(acc, path)

    cp.checkpoint_interval = INTERVAL
    return acc, cp


def new_top_rating(path='data_checkpoints/.checkpoints/tests'):
    acc = TopRatingAccumulator()
    cp = TopRatingCheckpoint(acc, path)

    cp.checkpoint_interval = INTERVAL
    return acc, cp


def new_message_interval():
    cp = MessagesCheckpoint(
        save_path='data_checkpoints/.checkpoints/tests/msgs')

    cp.checkpoint_interval = INTERVAL

    return cp


def filter_save_new_title(review_filter: ReviewFilter, cp: ReviewFilterCheckpoint, title: str, client_id: int):
    review_filter.add_title(title, client_id)
    cp.save(title, client_id)


def create_filter_with_books(client_id):
    review_filter, cp = new_filter()

    with open('data_checkpoints/test-datasets/reduced_books.csv') as f:
        for line in f:
            book = parse_book_from_client(line.strip())

            if not book:
                continue

            filter_save_new_title(review_filter, cp, book.title, client_id)

    return review_filter, cp


def gen_q_msg(i: int, client_id: int = 1):
    return BookMessage(f"Title {i}", i, client_id)


class TestCheckpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = []
        with open('data_checkpoints/test-datasets/reduced_books.csv') as f:
            for line in f:
                book = parse_book_from_client(line.strip())

                if not book:
                    continue

                cls.books.append(book)

    def test_wal_file_exist_after_state_checkpoint(self):
        r1, data_cp = new_filter()

        for client_id in range(CLIENTS):
            for i in range(data_cp.checkpoint_interval + 1):
                filter_save_new_title(r1, data_cp, f"Title {i}", client_id)

        for client_id in range(CLIENTS):
            self.assertTrue(os.path.exists(data_cp.wal_path(client_id)))

    def test_wal_file_exist_for_a_client_and_not_for_another(self):
        r1, data_cp = new_filter()

        client1 = 1
        client2 = 2

        for i in range(data_cp.checkpoint_interval + 1):
            filter_save_new_title(r1, data_cp, f"Title {i}", client1)

        for i in range(data_cp.checkpoint_interval):
            filter_save_new_title(r1, data_cp, f"Title {i}", client2)

        self.assertTrue(os.path.exists(data_cp.wal_path(client1)))
        self.assertFalse(os.path.exists(data_cp.wal_path(client2)))

    def test_wal_file_does_not_exist_after_state_checkpoint(self):
        r1, data_cp = new_filter()

        for client_id in range(CLIENTS):
            for i in range(data_cp.checkpoint_interval):
                filter_save_new_title(r1, data_cp, f"Title {i}", client_id)

        for client_id in range(CLIENTS):
            self.assertFalse(os.path.exists(data_cp.wal_path(client_id)))

    def test_checkpoint_file_does_not_exist(self):
        r1, data_cp = new_filter()
        for client_id in range(CLIENTS):
            for i in range(data_cp.checkpoint_interval // 2):
                filter_save_new_title(r1, data_cp, f"Title {i}", client_id)

        for client_id in range(CLIENTS):
            self.assertFalse(os.path.exists(
                data_cp.cp_path(client_id) + '.txt'))

    def test_recover_from_only_checkpoint(self):
        r1, data_cp = new_filter()

        for client_id in range(CLIENTS):
            for i in range(data_cp.checkpoint_interval):
                filter_save_new_title(r1, data_cp, f"Title {i}", client_id)

        r2, _ = new_filter()

        self.assertEqual(r1.titles, r2.titles)

    def test_recover_from_only_wal(self):
        r1, data_cp = new_filter()

        for client_id in range(CLIENTS):
            for i in range(data_cp.checkpoint_interval // 2):
                filter_save_new_title(r1, data_cp, f"Title {i}", client_id)

        r2, _ = new_filter()

        self.assertEqual(r1.titles, r2.titles)

    def test_recover_filter_from_correct_file(self):
        review_filter, _ = create_filter_with_books(1)

        review_filter2, _ = new_filter()

        self.assertEqual(review_filter2.titles, review_filter.titles)

    def test_recover_filter_from_a_corrupted_file(self):
        """
        Checkpoint intenta levantarse de un archivo corrupto, donde la escritura del cambio fue interrumpida
        Casos contemplados:
            * Se escribe el contenido del cambio a la mitad
            * Un cambio escrito correctamente
            * Solo se escribe la cantidad de caracteres del cambio
            * No se escribe la cantidad de caracteres por completo
            * Linea vacia
        """
        review_filter, _ = new_filter(
            'data_checkpoints/test-datasets/corrupted-wal')

        self.assertEqual(len(review_filter.titles), 1)

    def test_messages_checkpoint_saving_2_messages_throws_exception(self):
        msg_checkpoint = new_message_interval()
        msg1 = gen_q_msg(1, 1)
        msg2 = gen_q_msg(2, 1)
        msg_checkpoint.save(msg1)

        msg_checkpoint.save(msg2)
        msg_checkpoint.mark_msg_as_sent(msg2)

        self.assertFalse(msg_checkpoint.is_sent_msg(msg1))
        self.assertTrue(msg_checkpoint.is_sent_msg(msg2))

        msg_cp2 = new_message_interval()

        self.assertFalse(msg_cp2.is_sent_msg(msg1))
        self.assertTrue(msg_cp2.is_sent_msg(msg2))

    def test_messages_checkpoint_save_and_mark_msg_as_sent(self):
        msg_checkpoint = new_message_interval()
        for i in range(100):
            msg = gen_q_msg(i, 1)

            self.assertFalse(msg_checkpoint.is_processed_msg(msg))
            msg_checkpoint.save(msg)
            self.assertFalse(msg_checkpoint.is_sent_msg(msg))
            self.assertTrue(msg_checkpoint.is_processed_msg(msg))
            msg_checkpoint.mark_msg_as_sent(msg)
            self.assertTrue(msg_checkpoint.is_sent_msg(msg))

    def test_messages_checkpoint_load_from_cp(self):
        msg_cp = new_message_interval()

        for i in range(msg_cp.checkpoint_interval):
            msg = gen_q_msg(i, 1)
            msg_cp.save(msg)
            msg_cp.mark_msg_as_sent(msg)

        self.assertFalse(os.path.exists(msg_cp.wal_path(1)))
        self.assertTrue(os.path.exists(msg_cp.cp_path(1) + '.txt'))

        msg_cp2 = new_message_interval()

        for i in range(msg_cp.checkpoint_interval):
            msg = gen_q_msg(i, 1)
            self.assertTrue(msg_cp2.is_sent_msg(msg))

    def test_messages_checkpoint_load_from_wal(self):
        msg_cp = new_message_interval()
        for i in range(msg_cp.checkpoint_interval // 2):
            msg = gen_q_msg(i, 1)
            msg_cp.save(msg)
            msg_cp.mark_msg_as_sent(msg)

        self.assertTrue(os.path.exists(msg_cp.wal_path(1)))
        self.assertFalse(os.path.exists(msg_cp.cp_path(1) + '.txt'))

        msg_cp2 = new_message_interval()

        for i in range(msg_cp.checkpoint_interval // 2):
            msg = gen_q_msg(i, 1)
            self.assertTrue(msg_cp2.is_sent_msg(msg))

    def test_messages_checkpoint_load_from_wal_not_confirmed_message(self):
        msg_cp = new_message_interval()

        for i in range(msg_cp.checkpoint_interval):
            msg = gen_q_msg(i, 1)
            msg_cp.save(msg)
            msg_cp.mark_msg_as_sent(msg)

        msg_cp.save(gen_q_msg(msg_cp.checkpoint_interval, 1))

        msg_cp2 = new_message_interval()

        for i in range(msg_cp.checkpoint_interval):
            msg = gen_q_msg(i, 1)
            self.assertTrue(msg_cp2.is_sent_msg(msg))

        self.assertFalse(msg_cp2.is_sent_msg(
            gen_q_msg(msg_cp.checkpoint_interval, 1)))
        self.assertTrue(msg_cp2.is_processed_msg(
            gen_q_msg(msg_cp.checkpoint_interval, 1)))

    def test_messages_checkpoint_load_from_cp_not_confirmed_message(self):
        msg_cp = new_message_interval()

        for i in range(msg_cp.checkpoint_interval):
            msg = gen_q_msg(i, 1)
            msg_cp.save(msg)

            if i != msg_cp.checkpoint_interval - 1:
                msg_cp.mark_msg_as_sent(msg)

        msg_cp2 = new_message_interval()

        for i in range(msg_cp.checkpoint_interval - 1):
            msg = gen_q_msg(i, 1)

            self.assertTrue(msg_cp2.is_sent_msg(msg))

        self.assertFalse(msg_cp2.is_sent_msg(
            gen_q_msg(msg_cp.checkpoint_interval - 1, 1)))
        self.assertTrue(msg_cp2.is_processed_msg(
            gen_q_msg(msg_cp.checkpoint_interval - 1, 1)))

    def test_load_decades_accumulator_cp(self):
        acc, data_cp = new_acc()
        for client_id in range(CLIENTS):
            for i in range(int(data_cp.checkpoint_interval * 1.5)):
                digit = i % 10
                book = Book(
                    authors=f"A{i}", published_year=f"1{digit}{digit}{digit}")
                acc.add_book(book, client_id)
                data_cp.save(book, client_id)

        acc_2, data_cp_2 = new_acc()
        for client_id in range(CLIENTS):
            self.assertEqual(
                acc.authors[client_id], acc_2.authors[client_id])
            self.assertEqual(
                acc.completed_authors[client_id], acc_2.completed_authors[client_id])

    def test_load_reviews_counter_cp(self):
        counter, r_cp, b_cp, sent_titles_cp = new_reviews_counter()
        for client_id in range(CLIENTS):
            for i in range(int(r_cp.checkpoint_interval * 1.5)):
                book = Book(title=f"T{i}",
                            authors=f"A{i}")

                review = Review(book.title, i)
                counter.add_book(book, client_id)
                counter.add_review(review, client_id)
                b_cp.save(book, client_id)
                r_cp.save(review, client_id)
                sent_titles_cp.save(book.title, client_id)

        counter2, r_cp, b_cp, sent_titles_cp2 = new_reviews_counter()

        self.assertEqual(counter.books, counter2.books)
        self.assertEqual(counter.reviews, counter2.reviews)
        self.assertEqual(sent_titles_cp.titles, sent_titles_cp2.titles)

    def test_load_accumulator_cp(self):
        acc, data_cp = new_sentiment_score_acc()
        for client_id in range(CLIENTS):
            for i in range(int(data_cp.checkpoint_interval * 1.5)):
                acc.add_sentiment_score(f"T{i}", i, client_id)
                data_cp.save(f"T{i}", i, client_id)

        acc_2, data_cp_2 = new_sentiment_score_acc()
        self.assertEqual(acc.title_sentiment_score,
                         acc_2.title_sentiment_score)

    def test_load_top_rating_cp(self):
        acc, data_cp = new_top_rating()
        for client_id in range(CLIENTS):
            for i in range(int(data_cp.checkpoint_interval * 1.5)):
                acc.add_title(f"T{i}", i, client_id)
                data_cp.save(f"T{i}", i, client_id)

        acc_2, data_cp_2 = new_top_rating()
        self.assertEqual(acc.books,
                         acc_2.books)

    def test_delete_client(self):
        acc, data_cp = new_top_rating()
        for client_id in range(CLIENTS):
            for i in range(int(data_cp.checkpoint_interval * 1.5)):
                acc.add_title(f"T{i}", i, client_id)
                data_cp.save(f"T{i}", i, client_id)

        data_cp.delete_client(1)

        self.assertFalse(os.path.exists(f"{data_cp.path}/1"))
        self.assertTrue(os.path.exists(f"{data_cp.path}/0"))
        self.assertTrue(os.path.exists(f"{data_cp.path}/2"))

    def test_no_client_messages_after_delete(self):
        msg_cp = new_message_interval()
        for client_id in range(CLIENTS):
            for i in range(int(msg_cp.checkpoint_interval * 1.5)):
                msg = gen_q_msg(i, client_id)
                msg_cp.save(msg)
                msg_cp.mark_msg_as_sent(msg)

        msg_cp.delete_client(1)
        self.assertTrue(1 not in msg_cp.processed_messages)
        self.assertTrue(0 in msg_cp.processed_messages)
        self.assertTrue(2 in msg_cp.processed_messages)

    def test_no_titles_after_delete(self):
        counter, r_cp, b_cp, sent_titles_cp = new_reviews_counter()
        for client_id in range(CLIENTS):
            for i in range(int(sent_titles_cp.checkpoint_interval * 1.5)):
                book = Book(title=f"T{i}",
                            authors=f"A{i}")
                sent_titles_cp.save(book.title, client_id)

        sent_titles_cp.delete_client(1)
        self.assertTrue(1 not in sent_titles_cp.titles)
        self.assertTrue(0 in sent_titles_cp.titles)
        self.assertTrue(2 in sent_titles_cp.titles)

    def tearDown(self) -> None:
        try:
            shutil.rmtree('data_checkpoints/.checkpoints/tests')
        except FileNotFoundError:
            pass
        return super().tearDown()


if __name__ == '__main__':
    unittest.main()
