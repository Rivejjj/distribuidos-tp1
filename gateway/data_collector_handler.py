import socket
import logging
import signal
from utils.initialize import decode
from rabbitmq.queue import QueueMiddleware
from utils.parser import DATA_SEPARATOR, parse_query_msg
from utils.sockets import send_message


class DataCollectorHandler:
    def __init__(self, client_sock, query_count, input_queue, id):
        # Initialize server socket
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())

        self.client_sock = client_sock

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
        try:
            self.receiver_queue.start_consuming(self.handle_result())
        except OSError:
            self.stop()

    def stop(self):
        logging.info(
            '[DATA COLLECTOR] action: receive_termination_signal | result: in_progress')

        self._close_client_socket()

        self.receiver_queue.end()

        logging.info(
            f'[DATA COLLECTOR] action: receive_termination_signal | result: success')

    def _close_client_socket(self):
        logging.info(
            '[DATA COLLECTOR] action: closing client socket | result: in_progress')
        if self.client_sock:
            self.client_sock.close()
            self.client_sock = None

        logging.info(
            '[DATA COLLECTOR] action: closing client socket | result: success')

    def handle_result(self):
        def callback(ch, method, properties, body):
            try:
                logging.info(f"[QUERY RESULT]: {body}")
                msg = parse_query_msg(body)

                if msg.is_eof():
                    self.received_eofs += 1
                    logging.info(f"[FINAL] EOF received {self.received_eofs}")

                    if self.received_eofs >= self.query_count:
                        logging.info("All queries finished")
                        send_message(self.client_sock, "EOF")
                        self.received_eofs = 0
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                    return

                if msg.is_dc():
                    logging.info(f"Client disconnect {msg.get_client_id()}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    self.stop()
                    return

                logging.info(f"Received result {msg}")

                query = msg.get_query()

                if not query:
                    logging.error("No query found in message")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return

                client_data = msg.serialize_data().replace(DATA_SEPARATOR, ',')

                send_message(self.client_sock,
                             f"{query}:{client_data}".rstrip(','))

                ch.basic_ack(delivery_tag=method.delivery_tag)
            except OSError:
                self.stop()
        return callback


def create_data_collector_handler(client_socket, query_count, input_queue, client_id):
    c_handler = DataCollectorHandler(
        client_socket, query_count,  input_queue, client_id)

    c_handler.run()
