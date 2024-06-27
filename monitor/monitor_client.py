import socket
import logging
import time
import signal
from utils.sockets import receive, send_message
from utils.initialize import decode

TIME_TO_WAIT = 3

class MonitorClient():
    def __init__(self, name):
        signal.signal(signal.SIGTERM, lambda signal, frame: self.close())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', 22225))
        self.sock.listen()
        self.connected = False
        self.conn = None
        self.addr = None
        self.name = name
        self.running = True

    def listen_for_connections(self):
        while not self.connected:
            try:
                self.conn, self.addr = self.sock.accept()
            except OSError as e:
                logging.error(f"Error in client: {e}")
                break
            self.conn.settimeout(10)
            self.connected = True
            logging.warning(f"CONNECTED TO MONITOR!")

    def run(self):
        while self.running:
            self.listen_for_connections()
            while self.connected:
                try:
                    logging.warning(f"Sending heartbeat to monitor")
                    send_message(self.conn, self.name)
                    data = decode(receive(self.conn))
                    logging.warning(f"Answer from server: {data}")
                    time.sleep(TIME_TO_WAIT)
                except (socket.timeout, OSError, EOFError) as e:
                    logging.error(f"Error in client: {e}")
                    self.conn.close()
                    self.connected = False
                time.sleep(1)


    def restart_connection(self):
        logging.warning(f"Restarting connection")
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.address = None
        self.port = None
        time.sleep(1)
    
    def close(self):
        self.sock.close()
        self.connected = False
        self.running = False
