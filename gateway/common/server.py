import socket
import logging
import signal
from common.data_receiver import DataReceiver
from messages.book import Book
from messages.review import Review
from utils.initialize import encode
from rabbitmq.queue import QueueMiddleware
# CAMBIAR, NO COLGAR CON ESTO
MAX_BYTES = 1


class Server:
    def __init__(self, port, listen_backlog, input_queue=None, exchange=None):
        # Initialize server socket
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.client_sock = None
        self.queue = QueueMiddleware(
            [], input_queue=input_queue, exchange=exchange)

        self.receiving_books = True

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        while True:
            try:
                client_sock = self.__accept_new_connection()
                self.client_sock = client_sock
                self.__handle_client_connection()
            except OSError:
                break

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        data_receiver = DataReceiver()
        try:
            while True:

                msg = self.__safe_receive().decode().rstrip()
                print(f'msg: {msg}')
                if msg == "EOF":
                    print("EOF received")
                    self.queue.send_to_exchange(encode("EOF"))

                if msg == "":
                    break
                # addr = self.client_sock.getpeername()

                book = data_receiver.parse_book(msg)
                if book:
                    self.queue.send_to_exchange(encode(str(book)))
                    # print(f'sending to comp.filter | msg: {str(book)}')
                        
                review = data_receiver.parse_review(msg)
                if review:
                    self.queue.send_to_exchange(encode(str(review)))
                    # print(f'sending to comp.filter | msg: {str(review)}')

                # logging.info(
                    # f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
        except OSError as e:
            logging.error(
                f"action: receive_message | result: fail | error: {e}")
        finally:
            print("CLOSING")
            self._close_client_socket()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
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

    # def __safe_send(self, message):
    #     total_sent = 0
    #     bytes_to_send = message.encode('utf-8')

    #     while total_sent < len(message):
    #         n = self.client_sock.send(bytes_to_send[total_sent:])
    #         total_sent += n
    #     return

    def __safe_receive(self):
        # CAMBIAR ANTES DE ENTREGAR, NO COLGAR CON ESTO

        received_data = b''
        while True:
            chunk = self.client_sock.recv(MAX_BYTES)
            received_data += chunk
            if chunk == b'\n' or not chunk:
                break
        return received_data
