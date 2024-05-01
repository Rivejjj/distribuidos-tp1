import logging
import time
import pika
from utils.initialize import decode, encode

EOF_SEPARATOR = ":"
IDS_SEPARATOR = ","


class EOFQueue:
    def __init__(self, id: int, total_workers: int, eof_callback=None, all_nodes_received_eof_callback=None):
        logging.info("Connecting to queue")

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

        eof_send_queue = f"EOF_{(id + 1) % total_workers}"
        eof_receive_queue = f"EOF_{id}"

        self.eof_callback = eof_callback
        self.service_callback = None
        self.all_received_callback = all_nodes_received_eof_callback

        self.eof_send_queue = eof_send_queue
        self.eof_receive_queue = eof_receive_queue
        self.total_workers = total_workers
        self.id = id
        self.channel.queue_declare(queue=eof_receive_queue, durable=True)
        self.channel.queue_declare(queue=eof_send_queue, durable=True)

        self.channel.basic_consume(
            queue=eof_receive_queue, on_message_callback=self.eof_receive_queue_callback(), auto_ack=True)

        self.channel.basic_qos(prefetch_count=1)

        self.channel.start_consuming()

    def set_service_callback(self, service_callback):
        self.service_callback = service_callback

    def send(self, queue, message):
        self.channel.basic_publish(
            exchange='', routing_key=queue, body=message)

    def send_to_next(self, message):
        self.send(self.eof_send_queue, message)

    def propagate_eof(self, body):
        message = decode(body)

        split_msg = message.split(EOF_SEPARATOR)
        if len(split_msg) != 2:
            self.send(self.eof_send_queue,
                      f"{message}{EOF_SEPARATOR}{self.id}")
            return

        ids = split_msg[1].split(IDS_SEPARATOR)

        if len(ids) == self.total_workers or (self.id not in ids and len(ids) + 1 == self.total_workers):
            print("EOF reached")
            self.all_received_callback()
            return

        self.send_to_next(body +
                          encode(f"{IDS_SEPARATOR}{self.id}"))

    def eof_receive_queue_callback(self):
        def callback(ch, method, properties, body):
            if self.eof_callback:
                self.eof_callback(ch, method, properties, body)

            self.propagate_eof(body)
        return callback
