import socket
import logging
import signal
import threading
from common.data_receiver import DataReceiver
from messages.book import Book
from messages.review import Review
from utils.initialize import decode, encode
from rabbitmq.queue import QueueMiddleware
from utils.sockets import safe_receive, send_message, send_success


MAX_MESSAGE_BYTES = 16


class Server:
    def __init__(self, port, results_port, listen_backlog, query_count, input_queue=None, output_queues=[], id=0):
        # Initialize server socket
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self.results_server_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.results_server_socket.bind(('', results_port))
        self.results_server_socket.listen(listen_backlog)

        self.client_sock = None
        self.results_client_sock = None

        self.results_thread = None
        self.queue = QueueMiddleware(
            output_queues)

        self.receiver_queue = QueueMiddleware(
            [], input_queue=input_queue, id=id, wait_for_rmq=False)

        self.query_count = query_count

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        threading.Thread(target=self.run_results).start()
        threading.Thread(target=self.run_client).start()

    def run_client(self):
        while True:
            try:
                print(f"waiting for connection")
                client_sock = self.__accept_new_connection(self._server_socket)
                self.client_sock = client_sock
                self.handle_client_connection()
            except OSError:
                break

        self.client_sock.close()

    def run_results(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        while True:
            try:
                print(f"waiting for connection for results")
                client_sock = self.__accept_new_connection(
                    self.results_server_socket)

                print(f"results client sock: {client_sock}")
                self.results_client_sock = client_sock
                self.receiver_queue.start_consuming(self.handle_result())
            except OSError:
                break

        self.results_client_sock.close()

    def __accept_new_connection(self, socket):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = socket.accept()
        logging.info(
            f'action: accept_connections | result: success | ip: {addr[0]}')
        return c

    def stop(self):
        logging.info(
            'action: receive_termination_signal | result: in_progress')

        logging.info('action: closing listening socket | result: in_progress')
        self._server_socket.close()
        logging.info('action: closing listening socket | result: success')

        self._close_client_socket()

        logging.info(
            f'action: receive_termination_signal | result: success')

    def _close_client_socket(self):
        logging.info('action: closing client socket | result: in_progress')
        if self.client_sock:
            self.client_sock.close()
            self.client_sock = None
        logging.info('action: closing client socket | result: success')

    def __receive_message_length(self):
        try:
            int_bytes = safe_receive(self.client_sock,
                                     MAX_MESSAGE_BYTES)
            print("receiving message length", int_bytes)
            msg_length = int.from_bytes(int_bytes, "little")

            logging.info(
                f"action: receive_message_length | result: success | length: {msg_length}")

            send_success(self.client_sock)

            return msg_length
        except socket.error as e:
            logging.error(
                f"action: receive_message_length | result: failed | error: client disconnected")
            raise e
        except Exception as e:
            logging.error(
                f"action: receive_message_length | result: failed | error: {e}")
            raise e

    def handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:

            while True:
                msg_length = self.__receive_message_length()

                print(f"msg_length: {msg_length}")

                if msg_length == 0:
                    return

                msg = decode(safe_receive(
                    self.client_sock, msg_length)).rstrip()

                self.__process_message(msg)

                # self.__send_message(msg)

        except OSError as e:
            logging.error(
                f"action: receive_message | result: fail | error: {e}")
        except Exception as e:
            logging.error(
                f"action: any | result: fail | error: {e}")
        self._close_client_socket()

    def __process_message(self, msg):
        # addr = self.client_sock.getpeername()
        data_receiver = DataReceiver()

        print(f'received message: {msg}')

        if msg == "EOF":
            self.queue.send_eof(encode("EOF"))
            return

        book = data_receiver.parse_book(msg)
        if book:

            pool = [f"query{i}" for i in range(1, 5)]

            for name in pool:
                self.queue.send_to_pool(name, encode(str(book)), book.title)
            print(

                f'sending to comp.filter | msg: {str(book)}')
            return
        review = data_receiver.parse_review(msg)
        if review:
            pool = [f"query{i}" for i in range(3, 5)]

            for name in pool:
                self.queue.send_to_pool(
                    name, encode(str(review)), review.title)
            print(
                f'sending to comp.filter | msg: {str(review)}')
            return

        print(f'invalid message: {msg}')

    def handle_result(self):
        def callback(ch, method, properties, body):
            print(f"[QUERY RESULT]: {decode(body)}")
            msg = decode(body)
            print(self.client_sock)

            if msg == "EOF":
                self.query_count -= 1
                if self.query_count > 0:
                    return

            send_message(self.results_client_sock, msg)
        return callback

    def __send_message(self, msg):
        print(f'sending message: {msg}')
        send_message(self.client_sock, msg)
