import logging
import time
import pika


class Queue:
    def __init__(self, queue_names):
        logging.info("Connecting to queue")

        # Waits for rabbitmq
        time.sleep(10)

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq'))
        self.channel = self.connection.channel()
        for name in queue_names:
            logging.info("Declaring queue %s", name)
            self.channel.queue_declare(queue=name, durable=True)

    def start_consuming(self, name,  callback):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=name, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def end(self):
        self.connection.close()

    def send(self, name, message):
        self.channel.basic_publish(
            exchange='', routing_key=name, body=message, properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
