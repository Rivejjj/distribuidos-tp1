from multiprocessing import Process
import socket
import logging
import signal
from data_collector_handler import create_data_collector_handler
from utils.initialize import decode
from utils.sockets import receive


class DataCollector:
    def __init__(self, results_port, listen_backlog, query_count, input_queue=None):
        # Initialize server socket
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())

        self.results_server_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.results_server_socket.bind(('', results_port))
        self.results_server_socket.listen(listen_backlog)

        self.query_count = query_count
        self.input_queue = input_queue
        self.cur_client = 0
        self.processes = []

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

                client_id = int(decode(receive(client_sock)))

                logging.info(f"results client sock: {client_id}")
                process = Process(target=create_data_collector_handler,
                                  args=(client_sock, self.query_count, self.input_queue, self.cur_client))

                self.cur_client += 1
                self.processes.append(process)
                process.start()
            except OSError:
                break

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

        for process in self.processes:
            process.terminate()

        logging.info(
            f'action: receive_termination_signal | result: success')
