from multiprocessing import Process
import socket
import logging
import signal
from entities.sys_clean import SystemCleanMessage
from rabbitmq.queue import QueueMiddleware
from server_handler import create_server_handler
from utils.initialize import decode, encode
from utils.sockets import receive


class Server:
    def __init__(self, port, listen_backlog, output_queues=[]):
        # Initialize server socket
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

        self.output_queues = output_queues
        self.processes = []
        self.cur_client = 0

        self.queue = QueueMiddleware(output_queues)
        logging.info(f"Cleaning all saved states")
        self.queue.send_to_all(encode(SystemCleanMessage(0, -1)))
        self.queue.end()
        logging.info(f"Sent message, closing queue")

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        self.run_client()

    def run_client(self):
        while True:
            try:
                logging.info(f"waiting for connection")
                client_sock = self.__accept_new_connection(self._server_socket)

                client_id = int(decode(receive(client_sock)))

                logging.info(f"client sock: {client_id}")
                process = Process(target=create_server_handler,
                                  args=(client_sock, self.output_queues, self.cur_client))

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
        logging.info('action: closing listening socket | result: in_progress')
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        logging.info('action: closing listening socket | result: success')

        for process in self.processes:
            process.terminate()

        logging.info(f'action: receive_termination_signal | result: success')
