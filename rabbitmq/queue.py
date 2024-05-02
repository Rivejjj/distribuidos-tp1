import logging
import time
import pika

from utils.initialize import add_query_to_message, encode


class QueueMiddleware:
    def __init__(self, output_queues, input_queue=None, id=0, previous_workers=0, wait_for_rmq=True):
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
        self.__declare_output_queues(output_queues)

        if input_queue:
            self.__declare_input_queue(input_queue, id)

        self.channel.start_consuming()

        self.previous_workers = previous_workers
        self.received_eofs = 0

    def __calculate_queue_pools(self, output_queues):
        for name, worker_count in output_queues:
            logging.info(f"[QUEUE] Calculating queue pool for {name}")

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
        logging.info(f"Declaring input queue with params: {input_queue}, {id}")
        self.input_queue = f"{input_queue}_{id}"

        logging.info(f"[QUEUE] DECLARING INPUT QUEUE {self.input_queue}")

        self.channel.queue_declare(
            queue=self.input_queue, durable=True)

    def start_consuming(self, callback):
        if self.input_queue:
            self.channel.basic_consume(
                queue=self.input_queue, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def end(self):
        self.connection.close()

    def send(self, name, message):
        # logging.info(f"Sending message to queue {name}: {message}")
        self.channel.basic_publish(
            exchange='', routing_key=name, body=message, properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    def send_to_all(self, message):
        logging.info(f"[QUEUE] Sending message to all: {message}")

        for name in self.output_queues:
            logging.info(f"[QUEUE] Sending message to {name}")
            self.send(name, message)

    def send_to_all_except(self, message, except_queue):
        for name in self.output_queues:
            if name != except_queue:
                self.send(name, message)

    def send_eof(self, callback=None):
        msg = "EOF"

        self.received_eofs += 1
        logging.info(f"[QUEUE] Received EOFs {self.received_eofs}")

        if self.previous_workers <= self.received_eofs:
            logging.info("[QUEUE] Received EOFs of all workers")
            self.received_eofs = 0

            if callback:
                print("[QUEUE] Executing callback")
                callback()
            self.send_to_all(encode(msg))

            print(
                f"[QUEUE] Sending EOF to next workers {self.output_queues}")
            return True

        return False

    def __get_worker_name(self, name, worker):
        return f"{name}_{worker}"

    def __calculate_worker(self, next_pool_name, hash_key):
        output_queues = list(filter(
            lambda output_queue: next_pool_name in output_queue, self.output_queues))

        hash_value = hash(hash_key)
        # print(f"[QUEUE] Calculating worker for {next_pool_name} with hash {hash_value}")
        return hash_value % len(output_queues)

    def send_to_pool(self, message, hash_key, next_pool_name=None):
        if not next_pool_name and len(self.queue_pools) == 1:
            next_pool_name = list(self.queue_pools.keys())[0]
        next = self.__calculate_worker(next_pool_name, hash_key)

        queue_name = self.__get_worker_name(next_pool_name, next)

        # print(f"[QUEUE] Sending message to {queue_name}: {message}")
        self.send(queue_name, message)
