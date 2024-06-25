

import logging
import signal

import pika

from entities.eof_msg import EOFMessage
from entities.query_message import QueryMessage
from rabbitmq.eofs_cp import ReceivedEOF
from utils.initialize import encode, uuid

RESULTS_QUEUE = 'results'


class QueueMiddleware:
    def __init__(self, output_queues, input_queue=None, id=0, previous_workers=0, save_to_file=True):
        signal.signal(signal.SIGTERM, lambda signal, frame: self.end())
        # logging.info("Connecting to queue: queue_names=%s", queue_names)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        logging.info("Connected to queue")
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)

        self.input_queue = None

        self.queue_pools = {}

        self.__calculate_queue_pools(output_queues)

        self.output_queues = []

        self.result_queue = None

        if (RESULTS_QUEUE, 1) in output_queues:
            output_queues.remove((RESULTS_QUEUE, 1))
            self.__declare_result_queue()
        self.__declare_output_queues(output_queues)

        if input_queue:
            self.__declare_input_queue(input_queue, id)

        self.channel.start_consuming()

        self.received_eofs_cp = ReceivedEOF(
            previous_workers, save_to_file=save_to_file)

    def __calculate_queue_pools(self, output_queues):
        for name, worker_count in output_queues:
            # logging.info(f"[QUEUE] Calculating queue pool for {name}")

            self.queue_pools[name] = worker_count

    def __declare_output_queues(self, output_queues):
        for name, worker_count in output_queues:
            logging.info(f"[QUEUE] DECLARING QUEUE POOL {name}")
            for i in range(worker_count):
                queue_name = self.__get_worker_name(name, i)
                logging.info(f"[QUEUE] DECLARING QUEUE {queue_name}")
                self.channel.queue_declare(queue=queue_name, durable=True)
                self.output_queues.append(queue_name)

    def __declare_input_queue(self, input_queue, id):

        if input_queue == RESULTS_QUEUE:
            self.channel.exchange_declare(
                exchange=RESULTS_QUEUE, exchange_type='direct')

            result = self.channel.queue_declare(queue='', exclusive=True)
            self.input_queue = result.method.queue

            self.channel.queue_bind(
                exchange=RESULTS_QUEUE, queue=self.input_queue, routing_key=str(id))
        else:
            logging.info(
                f"Declaring input queue with params: {input_queue}, {id}")
            self.input_queue = f"{input_queue}_{id}"

            logging.info(f"[QUEUE] DECLARING INPUT QUEUE {self.input_queue}")

            self.channel.queue_declare(
                queue=self.input_queue, durable=True)

    def start_consuming(self, callback):
        if self.input_queue:
            self.channel.basic_consume(
                queue=self.input_queue, on_message_callback=callback, auto_ack=False)
        self.channel.start_consuming()

    def end(self):
        if self.channel.is_open:
            self.channel.stop_consuming()
            self.channel.close()
        if self.connection.is_open:
            self.connection.close()
        logging.info("Connection and channel closed gracefully")

    def send(self, name, message):
        # logging.info(f"Sending message to queue {name}: {message}")
        if self.channel.is_open:
            self.channel.basic_publish(
                exchange='', routing_key=name, body=message, properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))

    def send_to_all(self, message):
        # logging.info(f"[QUEUE] Sending message to all: {message}")

        for name in self.output_queues:
            logging.info(f"[QUEUE] Sending message {message} to {name}")
            self.send(name, message)

    def send_to_all_except(self, message, except_queue):
        for name in self.output_queues:
            if name != except_queue:
                self.send(name, message)

    def send_eof(self, msg: EOFMessage, callback=None):
        client_id = msg.get_client_id()
        self.received_eofs_cp.save(msg.get_client_id())

        logging.info(
            f"[QUEUE] Received EOFs {self.received_eofs_cp.eofs[client_id]} for client {client_id}")

        if self.received_eofs_cp.eof_reached(client_id):
            logging.info(
                f"[QUEUE] Received EOFs of all workers for client {client_id}")

            if callback:
                logging.info("[QUEUE] Executing callback")
                callback()

            id = uuid()
            logging.info(f"[QUEUE] Created uuid {id}")
            msg = EOFMessage(id, client_id)
            self.send_to_all(encode(msg))
            self.send_to_result(msg)
            logging.info(
                f"[QUEUE] Sending EOF to next workers {self.output_queues}")

            self.received_eofs_cp.clear(msg)

            return True

        return False

    def __get_worker_name(self, name, worker):
        return f"{name}_{worker}"

    def __calculate_worker(self, next_pool_name, hash_key):
        output_queues = list(filter(
            lambda output_queue: next_pool_name in output_queue, self.output_queues))

        hash_value = hash(hash_key)
        return hash_value % len(output_queues)

    def send_to_pool(self, message, hash_key, next_pool_name=None):
        if not next_pool_name and len(self.queue_pools) == 1:
            next_pool_name = list(self.queue_pools.keys())[0]
        next = self.__calculate_worker(next_pool_name, hash_key)

        queue_name = self.__get_worker_name(next_pool_name, next)

        self.send(queue_name, message)

    def handle_sigterm(self, signal, frame):
        logging.info("Received SIGTERM - shutting gracefully")
        self.end()
        return

    def __declare_result_queue(self):
        logging.info("DECLARING EXCHANGE")
        self.channel.exchange_declare(
            exchange=RESULTS_QUEUE, exchange_type='direct')

        self.result_queue = RESULTS_QUEUE

    def send_to_result(self, message: QueryMessage):
        if self.result_queue:
            logging.info(f"Sending to result exchange {message}")
            self.channel.basic_publish(
                exchange=RESULTS_QUEUE, routing_key=str(message.get_client_id()), body=encode(message))

    def delete_client(self, msg: QueryMessage):
        # self.send_to_all(encode(msg))
        self.received_eofs_cp.clear(msg)
