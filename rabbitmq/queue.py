import logging
import time
import pika
from utils.initialize import decode, encode

EOF_SEPARATOR = ":"
IDS_SEPARATOR = ","


class QueueMiddleware:
    def __init__(self, queue_names: list[(str, bool)], id=None, total_workers=None):
        logging.info("Connecting to queue")

        # Waits for rabbitmq
        time.sleep(10)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()

        self.output_queues = [
            name for (name, is_output) in queue_names if is_output]

        logging.info(queue_names)
        for (name, _) in queue_names:
            self.channel.queue_declare(queue=name, durable=True)

        if id:
            eof_send_queue = f"EOF_{(id + 1) % total_workers}"
            eof_receive_queue = f"EOF_{id}"

            self.eof_send_queue = eof_send_queue
            self.eof_receive_queue = eof_receive_queue
            self.total_workers = total_workers
            self.id = id
            self.channel.queue_declare(queue=eof_receive_queue, durable=True)
            self.channel.queue_declare(queue=eof_send_queue, durable=True)

            self.channel.basic_consume(
                queue=eof_receive_queue, on_message_callback=self.eof_receive_queue_callback(), auto_ack=True)

    def start_consuming(self, name, callback, eof_callback=None):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=name, on_message_callback=self.handle_message(callback, eof_callback), auto_ack=True)
        self.channel.start_consuming()

    def end(self):
        self.connection.close()

    def send_to_all(self, message):
        for queue in self.output_queues:
            self.send(queue, message)

    def send(self, name, message):
        logging.info(f"Sending message to {name}")
        self.channel.basic_publish(
            exchange='', routing_key=name, body=message, properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    def handle_message(self, service_callback, eof_callback=None):
        def callback(ch, method, properties, body):
            if decode(body) == "EOF":
                if eof_callback:
                    eof_callback(ch, method, properties, body)

                if self.eof_send_queue:
                    self.propagate_eof(body)
            else:
                service_callback(ch, method, properties, body)

        return callback

    def propagate_eof(self, body):
        message = decode(body)

        split_msg = message.split(EOF_SEPARATOR)
        if len(split_msg) != 2:
            self.send(self.eof_send_queue,
                      f"{message}{EOF_SEPARATOR}{self.id}")
            return

        ids = split_msg[1].split(IDS_SEPARATOR)

        if len(ids) == self.total_workers or (self.id not in ids and len(ids) + 1 == self.total_workers):
            self.send_eof()
            return

        self.send(self.eof_send_queue, body +
                  encode(f"{IDS_SEPARATOR}{self.id}"))

    def eof_receive_queue_callback(self):
        def callback(ch, method, properties, body):
            self.propagate_eof(body)
        return callback

    def send_eof(self):
        for queue in self.output_queues:
            self.send(queue, encode("EOF"))
