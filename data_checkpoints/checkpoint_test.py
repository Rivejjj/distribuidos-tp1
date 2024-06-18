import os
import unittest
import shutil

from data_checkpoints.messages_checkpoint import MessagesCheckpoint
from data_processors.book_filter.review_filter_checkpoint import ReviewFilterCheckpoint
from data_processors.book_filter.review_filter import ReviewFilter
from gateway.client_parser import parse_book_from_client


def new_filter(path='data_checkpoints/.checkpoints/tests'):
    review_filter = ReviewFilter()
    cp = ReviewFilterCheckpoint(
        review_filter, path)
    return review_filter, cp


def filter_save_new_title(review_filter: ReviewFilter, cp: ReviewFilterCheckpoint, title: str):
    review_filter.add_title(title)
    cp.save(title)


def create_filter_with_books():
    review_filter, cp = new_filter()

    with open('data_checkpoints/test-datasets/reduced_books.csv') as f:
        for line in f:
            book = parse_book_from_client(line.strip())

            if not book:
                continue

            filter_save_new_title(review_filter, cp, book.title)

    return review_filter, cp


class TestCheckpoints(unittest.TestCase):

    def test_wal_file_does_not_exist_after_state_checkpoint(self):
        r1, data_cp = new_filter()

        for i in range(data_cp.checkpoint_interval):
            filter_save_new_title(r1, data_cp, f"Title {i}")

        self.assertFalse(os.path.exists(data_cp.wal_path))

    def test_wal_file_exist_after_state_checkpoint(self):
        r1, data_cp = new_filter()

        for i in range(data_cp.checkpoint_interval + 1):
            filter_save_new_title(r1, data_cp, f"Title {i}")

        self.assertTrue(os.path.exists(data_cp.wal_path))

    def test_checkpoint_file_does_not_exist(self):
        r1, data_cp = new_filter()

        for i in range(data_cp.checkpoint_interval // 2):
            filter_save_new_title(r1, data_cp, f"Title {i}")

        self.assertFalse(os.path.exists(data_cp.cp_path + '.txt'))

    def test_recover_from_only_checkpoint(self):
        r1, data_cp = new_filter()

        for i in range(data_cp.checkpoint_interval):
            filter_save_new_title(r1, data_cp, f"Title {i}")

        r2, _ = new_filter()

        self.assertEqual(r1.titles, r2.titles)

    def test_recover_from_only_wal(self):
        r1, data_cp = new_filter()

        for i in range(data_cp.checkpoint_interval // 2):
            filter_save_new_title(r1, data_cp, f"Title {i}")

        r2, _ = new_filter()

        self.assertEqual(r1.titles, r2.titles)

    def test_recover_filter_from_correct_file(self):
        review_filter, _ = create_filter_with_books()

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
        msg_checkpoint = MessagesCheckpoint(
            save_path='data_checkpoints/.checkpoints/tests/msgs')

        msg_checkpoint.save(str(1))

        self.assertRaises(Exception, lambda: msg_checkpoint.save(str(2)))

    def test_messages_checkpoint_save_and_mark_msg_as_sent(self):
        msg_checkpoint = MessagesCheckpoint(
            save_path='data_checkpoints/.checkpoints/tests/msgs')

        for i in range(100):
            self.assertFalse(msg_checkpoint.is_processed_msg(str(i)))

            msg_checkpoint.save(str(i))
            self.assertFalse(msg_checkpoint.is_sent_msg(str(i)))
            self.assertTrue(msg_checkpoint.is_processed_msg(str(i)))
            msg_checkpoint.mark_msg_as_sent(str(i))
            self.assertTrue(msg_checkpoint.is_sent_msg(str(i)))

    def test_messages_checkpoint_load_from_cp(self):
        msg_cp = MessagesCheckpoint(
            save_path='data_checkpoints/.checkpoints/tests/msgs')

        for i in range(msg_cp.checkpoint_interval):

            msg_cp.save(str(i))
            msg_cp.mark_msg_as_sent(str(i))

        self.assertFalse(os.path.exists(msg_cp.wal_path))
        self.assertTrue(os.path.exists(msg_cp.cp_path + '.txt'))

        msg_cp2 = MessagesCheckpoint(
            save_path='data_checkpoints/.checkpoints/tests/msgs')

        for i in range(100):
            self.assertTrue(msg_cp2.is_sent_msg(str(i)))

    def test_messages_checkpoint_load_from_wal(self):
        msg_cp = MessagesCheckpoint(
            save_path='data_checkpoints/.checkpoints/tests/msgs')

        for i in range(msg_cp.checkpoint_interval // 2):

            msg_cp.save(str(i))
            msg_cp.mark_msg_as_sent(str(i))

        self.assertTrue(os.path.exists(msg_cp.wal_path))
        self.assertFalse(os.path.exists(msg_cp.cp_path + '.txt'))

        msg_cp2 = MessagesCheckpoint(
            save_path='data_checkpoints/.checkpoints/tests/msgs')

        for i in range(msg_cp.checkpoint_interval // 2):
            self.assertTrue(msg_cp2.is_sent_msg(str(i)))

    def test_messages_checkpoint_load_from_wal_not_confirmed_message(self):
        msg_cp = MessagesCheckpoint(
            save_path='data_checkpoints/.checkpoints/tests/msgs')

        for i in range(msg_cp.checkpoint_interval):

            msg_cp.save(str(i))
            msg_cp.mark_msg_as_sent(str(i))

        msg_cp.save(str(msg_cp.checkpoint_interval))

        msg_cp2 = MessagesCheckpoint(
            save_path='data_checkpoints/.checkpoints/tests/msgs')

        for i in range(msg_cp.checkpoint_interval):
            self.assertTrue(msg_cp2.is_sent_msg(str(i)))

        self.assertFalse(msg_cp2.is_sent_msg(str(msg_cp.checkpoint_interval)))
        self.assertTrue(msg_cp2.is_processed_msg(
            str(msg_cp.checkpoint_interval)))

    def test_messages_checkpoint_load_from_cp_not_confirmed_message(self):
        msg_cp = MessagesCheckpoint(
            save_path='data_checkpoints/.checkpoints/tests/msgs')

        for i in range(msg_cp.checkpoint_interval):
            msg_cp.save(str(i))

            if i != msg_cp.checkpoint_interval - 1:
                msg_cp.mark_msg_as_sent(str(i))

        msg_cp2 = MessagesCheckpoint(
            save_path='data_checkpoints/.checkpoints/tests/msgs')

        for i in range(msg_cp.checkpoint_interval - 1):
            self.assertTrue(msg_cp2.is_sent_msg(str(i)))

        self.assertFalse(msg_cp2.is_sent_msg(
            str(msg_cp.checkpoint_interval - 1)))
        self.assertTrue(msg_cp2.is_processed_msg(
            str(msg_cp.checkpoint_interval - 1)))

    def test_decades_recover_from_only_checkpoint(self):
        r1, data_cp = new_filter()

        for i in range(data_cp.checkpoint_interval):
            filter_save_new_title(r1, data_cp, f"Title {i}")

        r2, _ = new_filter()

        self.assertEqual(r1.titles, r2.titles)

    def test_decades_recover_from_only_wal(self):
        r1, data_cp = new_filter()

        for i in range(data_cp.checkpoint_interval // 2):
            filter_save_new_title(r1, data_cp, f"Title {i}")

        r2, _ = new_filter()

        self.assertEqual(r1.titles, r2.titles)

    def test_decades_recover_filter_from_correct_file(self):
        review_filter, _ = create_filter_with_books()

        review_filter2, _ = new_filter()

        self.assertEqual(review_filter2.titles, review_filter.titles)

    def test_decades_recover_filter_from_a_corrupted_file(self):
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

    def tearDown(self) -> None:
        try:
            shutil.rmtree('data_checkpoints/.checkpoints/tests')
        except FileNotFoundError:
            pass
        return super().tearDown()


if __name__ == '__main__':
    unittest.main()
