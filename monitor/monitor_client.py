import socket
import logging
import time
import signal
from utils.sockets import receive, send_message
from utils.initialize import decode
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
            self.conn, self.addr = self.sock.accept()
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
                    # self.conn.send(bytes(self.name, 'utf-8'))
                    data = decode(receive(self.conn))
                    # read = self.conn.recv(1024)
                    # if read == b'':
                    #     self.listen_for_connections()
                    logging.warning(f"Answer from server: {data}")
                    time.sleep(3)
                except (socket.timeout, OSError) as e:
                    logging.error(f"Error in client: {e}")
                    self.conn.close()
                    self.connected = False
                    break
                time.sleep(1)


    def restart_connection(self):
        logging.warning(f"Restarting connection")
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.address = None
        self.port = None
        self.connect()
        time.sleep(1)
    
    def close(self):
        self.sock.close()
        self.connected = False
        self.running = False
