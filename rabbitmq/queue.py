import logging
import time
import pika

from utils.initialize import encode


class QueueMiddleware:
    def __init__(self, output_queues: list[str], input_queue=None, exchange=None, wait_for_rmq=True):
        # logging.info("Connecting to queue: queue_names=%s", queue_names)

        # Waits for rabbitmq
        if wait_for_rmq:
            time.sleep(40)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        logging.info("Connected to queue")
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.exchange_queue_name = None
        self.input_queue = None

        self.output_queues = output_queues
        for name in output_queues:
            print("Declaring queue %s", name)
            self.channel.queue_declare(queue=name, durable=True)

        if exchange:
            self.exchange = exchange
            self.channel.exchange_declare(
                exchange=exchange, exchange_type='fanout')

            if not input_queue:
                print("Declaring exchange queue")
                result = self.channel.queue_declare(
                    queue='', durable=True)
                queue_name = result.method.queue

                self.exchange_queue_name = queue_name
                self.channel.queue_bind(
                    exchange=exchange, queue=queue_name)
                # self.channel.basic_consume(
                #     queue=queue_name, on_message_callback=callback, auto_ack=True)

        if input_queue:
            print("Declaring input queue")
            self.input_queue = input_queue

            self.channel.queue_declare(queue=input_queue, durable=True)
            # self.channel.basic_consume(
            #     queue=input_queue, on_message_callback=callback, auto_ack=True)

        self.channel.start_consuming()

    def start_consuming(self, callback):
        if self.input_queue:
            self.channel.basic_consume(
                queue=self.input_queue, on_message_callback=callback, auto_ack=True)
        if self.exchange_queue_name:
            self.channel.basic_consume(
                queue=self.exchange_queue_name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def end(self):
        self.connection.close()

    def send(self, name, message):
        # logging.info(f"Sending message to queue {name}: {message}")
        self.channel.basic_publish(
            exchange='', routing_key=name, body=message, properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))

    def send_to_exchange(self, message, routing_key=''):
        # logging.info(f"Sending message to exchange: {message}")
        if message == "EOF":
            print("EOF to exchange")

        self.channel.basic_publish(
            exchange=self.exchange, routing_key=routing_key, body=message)

    def send_to_all(self, message):
        print(f"[QUEUE] Sending message to all: {message}")
        for name in self.output_queues:
            self.send(name, message)

    def send_to_all_except(self, message, except_queue):
        for name in self.output_queues:
            if name != except_queue:
                self.send(name, message)

    def send_eof(self):
        print("[QUEUE] Sending EOF")
        self.send_to_all(encode("EOF"))
