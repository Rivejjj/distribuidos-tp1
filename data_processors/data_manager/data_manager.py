from abc import ABC, abstractmethod
from functools import partial
import logging
import os
import signal

from data_checkpoints.messages_checkpoint import MessagesCheckpoint
from entities.client_dc import ClientDCMessage
from entities.eof_msg import EOFMessage
from entities.query_message import QueryMessage
from rabbitmq.queue import QueueMiddleware
from utils.initialize import encode, get_queue_names
from utils.monitor import start_monitor_process
from utils.parser import parse_query_msg


class DataManager(ABC):
    def __init__(self, config_params):
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())

        self.messages_cp = MessagesCheckpoint('.checkpoints/msgs')

        if 'no-queue' not in config_params:
            self.queue_middleware = QueueMiddleware(get_queue_names(
                config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

        self.query = config_params["query"]
        self.processed_messages = {}

        self.monitor_process = start_monitor_process(config_params["name"])

    def stop(self):
        self.monitor_process.terminate()
        self.monitor_process.join()

    def run(self):
        try:
            self.queue_middleware.start_consuming(
                self.process_message())
        except Exception as e :
            logging.error(f"Error in start consuming: {e}")

    def eof_cb(self, eof_msg: EOFMessage):
        """
        Metodo que se llama al cumplir los requerimientos del eof
        """
        self.delete_client(eof_msg)

    @abstractmethod
    def send_to_next_worker(self, result):
        """
        Envia el resultado del procesamiento al siguiente pool de workers
        """
        pass

    @abstractmethod
    def process_query_message(self, msg: QueryMessage):
        """
        Procesa la query message despues de haberse validado
        Tiene que tener en cuenta que el mensaje pueda ya estar procesado, simplemente tiene que enviarlo al siguiente worker
        """
        pass

    def delete_client(self, msg: QueryMessage):
        """
        Borra el cliente
        """
        self.queue_middleware.delete_client(msg)
        self.messages_cp.delete_client(msg)

    def process_eof(self, eof_msg: EOFMessage):
        self.queue_middleware.send_eof(eof_msg, partial(self.eof_cb, eof_msg))

    def process_message(self):
        """
        Metodo que se llama al recibir un mensaje
        """
        def callback(ch, method, properties, body):
            msg = parse_query_msg(body)

            client_id = msg.get_client_id()

            self.processed_messages[client_id] = self.processed_messages.get(
                client_id, set())

            if msg.is_eof():
                logging.info(f"Received EOF of client {msg.get_client_id()}")
                self.process_eof(msg)
                if ch.is_open:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    logging.error(f"Error sending ack: Channel is closed")
                return

            if msg.is_dc():
                logging.info(
                    f"Received Client disconnect {msg.get_client_id()}")
                self.delete_client(msg)
                self.queue_middleware.send_to_all(encode(msg))
                if ch.is_open:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    logging.error(f"Error sending ack: Channel is closed")
                return

            if msg.is_sys_clean():
                logging.info(
                    f"Received System disconnect")
                self.delete()
                self.queue_middleware.send_to_all(encode(msg))
                if ch.is_open:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    logging.error(f"Error sending ack: Channel is closed")
                return

            if self.messages_cp.is_sent_msg(msg):
                logging.info(f"Already proccessed message {msg.get_id()}")
                if ch.is_open:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    logging.error(f"Error sending ack: Channel is closed")
                return

            logging.info(
                f"Received message: {msg.get_id()}")

            result = self.process_query_message(msg)

            self.messages_cp.save(msg)

            if result:
                self.send_to_next_worker(result)

            self.messages_cp.mark_msg_as_sent(msg)

            if ch.is_open:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                logging.error(f"Error sending ack: Channel is closed")
                return
        return callback

    def clients(self):
        if not os.path.exists(self.messages_cp.path):
            return
        clients = os.listdir(self.messages_cp.path)
        logging.info(f"Current clients: {clients}")
        return clients

    def delete(self):
        clients = self.clients()

        if not clients:
            return

        for client in clients:
            client_dc_msg = ClientDCMessage(0, int(client))
            self.delete_client(client_dc_msg)
        return
