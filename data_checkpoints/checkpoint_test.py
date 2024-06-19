import os
import unittest
import shutil

from data_checkpoints.messages_checkpoint import MessagesCheckpoint
from data_processors.book_filter.review_filter_checkpoint import ReviewFilterCheckpoint
from data_processors.book_filter.review_filter import ReviewFilter
from entities.book_msg import BookMessage
from gateway.client_parser import parse_book_from_client

CLIENTS = 3
INTERVAL = 100


def new_filter(path='data_checkpoints/.checkpoints/tests'):
    review_filter = ReviewFilter()
    cp = ReviewFilterCheckpoint(
        review_filter, path)

    cp.checkpoint_interval = INTERVAL
    return review_filter, cp


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

    def test_wal_file_does_not_exist_after_state_checkpoint(self):
        r1, data_cp = new_filter()

        for client_id in range(CLIENTS):
            for i in range(data_cp.checkpoint_interval + 1 // CLIENTS):
                filter_save_new_title(r1, data_cp, f"Title {i}", client_id)

        self.assertFalse(os.path.exists(data_cp.wal_path))

    def test_wal_file_exist_after_state_checkpoint(self):
        r1, data_cp = new_filter()

        for client_id in range(CLIENTS):
            for i in range(data_cp.checkpoint_interval // CLIENTS):
                filter_save_new_title(r1, data_cp, f"Title {i}", client_id)

        self.assertTrue(os.path.exists(data_cp.wal_path))

    def test_checkpoint_file_does_not_exist(self):
        r1, data_cp = new_filter()
        for client_id in range(CLIENTS):
            for i in range(data_cp.checkpoint_interval // 2 // CLIENTS):
                filter_save_new_title(r1, data_cp, f"Title {i}", client_id)

        self.assertFalse(os.path.exists(data_cp.cp_path + '.txt'))

    def test_recover_from_only_checkpoint(self):
        r1, data_cp = new_filter()

        for client_id in range(CLIENTS):
            for i in range(data_cp.checkpoint_interval // CLIENTS):
                filter_save_new_title(r1, data_cp, f"Title {i}", client_id)

        r2, _ = new_filter()

        self.assertEqual(r1.titles, r2.titles)

    def test_recover_from_only_wal(self):
        r1, data_cp = new_filter()

        for client_id in range(CLIENTS):
            for i in range(data_cp.checkpoint_interval // 2 // CLIENTS):
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

        self.assertRaises(Exception, lambda: msg_checkpoint.save(msg2))

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

        self.assertFalse(os.path.exists(msg_cp.wal_path))
        self.assertTrue(os.path.exists(msg_cp.cp_path + '.txt'))

        msg_cp2 = new_message_interval()

        for i in range(100):
            msg = gen_q_msg(i, 1)
            self.assertTrue(msg_cp2.is_sent_msg(msg))

    def test_messages_checkpoint_load_from_wal(self):
        msg_cp = new_message_interval()
        for i in range(msg_cp.checkpoint_interval // 2):
            msg = gen_q_msg(i, 1)
            msg_cp.save(msg)
            msg_cp.mark_msg_as_sent(msg)

        self.assertTrue(os.path.exists(msg_cp.wal_path))
        self.assertFalse(os.path.exists(msg_cp.cp_path + '.txt'))

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

    # def test_decades_recover_from_only_checkpoint(self):
    #     r1, data_cp = new_filter()

    #     for i in range(data_cp.checkpoint_interval):
    #         filter_save_new_title(r1, data_cp, f"Title {i}")

    #     r2, _ = new_filter()

    #     self.assertEqual(r1.titles, r2.titles)

    # def test_decades_recover_from_only_wal(self):
    #     r1, data_cp = new_filter()

    #     for i in range(data_cp.checkpoint_interval // 2):
    #         filter_save_new_title(r1, data_cp, f"Title {i}")

    #     r2, _ = new_filter()

    #     self.assertEqual(r1.titles, r2.titles)

    # def test_decades_recover_filter_from_correct_file(self):
    #     review_filter, _ = create_filter_with_books()

    #     review_filter2, _ = new_filter()

    #     self.assertEqual(review_filter2.titles, review_filter.titles)

    # def test_decades_recover_filter_from_a_corrupted_file(self):
    #     """
    #     Checkpoint intenta levantarse de un archivo corrupto, donde la escritura del cambio fue interrumpida
    #     Casos contemplados:
    #         * Se escribe el contenido del cambio a la mitad
    #         * Un cambio escrito correctamente
    #         * Solo se escribe la cantidad de caracteres del cambio
    #         * No se escribe la cantidad de caracteres por completo
    #         * Linea vacia
    #     """
    #     review_filter, _ = new_filter(
    #         'data_checkpoints/test-datasets/corrupted-wal')

    #     self.assertEqual(len(review_filter.titles), 1)

    def tearDown(self) -> None:
        try:
            shutil.rmtree('data_checkpoints/.checkpoints/tests')
        except FileNotFoundError:
            pass
        return super().tearDown()


if __name__ == '__main__':
    unittest.main()
