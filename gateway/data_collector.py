import socket
import logging
import signal
from utils.initialize import decode
from rabbitmq.queue import QueueMiddleware
from utils.parser import parse_query_msg
from utils.sockets import send_message


class DataCollector:
    def __init__(self, results_port, listen_backlog, query_count, input_queue=None, id=0):
        # Initialize server socket
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())

        self.results_server_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.results_server_socket.bind(('', results_port))
        self.results_server_socket.listen(listen_backlog)

        self.client_sock = None

        self.receiver_queue = QueueMiddleware(
            [], input_queue=input_queue, id=id)

        self.query_count = query_count
        self.received_eofs = 0

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        while True:
            try:
                logging.info(f"waiting for connection for results")
                client_sock = self.__accept_new_connection(
                    self.results_server_socket)

                logging.info(f"results client sock: {client_sock}")
                self.client_sock = client_sock
                self.receiver_queue.start_consuming(self.handle_result())
            except OSError:
                break

        self.client_sock.close()

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
        self.results_server_socket.close()
        logging.info('action: closing listening socket | result: success')

        self._close_client_socket()

        self.receiver_queue.end()

        logging.info(
            f'action: receive_termination_signal | result: success')

    def _close_client_socket(self):
        logging.info('action: closing client socket | result: in_progress')
        if self.client_sock:
            self.client_sock.close()
            self.client_sock = None
        logging.info('action: closing client socket | result: success')

    def handle_result(self):
        def callback(ch, method, properties, body):
            logging.info(f"[QUERY RESULT]: {decode(body)}")
            msg = decode(body).strip()

            # logging.info(self.client_sock)

            if msg == "EOF":
                self.received_eofs += 1
                logging.info(f"[FINAL] EOF received {self.received_eofs}")

                if self.received_eofs >= self.query_count:
                    logging.info("All queries finished")
                    send_message(self.client_sock, "EOF")
                    self.received_eofs = 0
                return

            _, data = parse_query_msg(msg)

            send_message(self.client_sock, data)
        return callback
