import socket
import logging
import time
import signal

class MonitorClient():
    def __init__(self, name):
        signal.signal(signal.SIGTERM, lambda signal, frame: self.close())
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', 22225))
        self.sock.listen()
        self.sock.settimeout(10)
        self.connected = False
        self.conn = None
        self.addr = None
        self.name = name
        self.running = True

    def listen_for_connections(self):
        while not self.connected:
            self.conn, self.addr = self.sock.accept()
            self.connected = True
            logging.warning(f"CONNECTED TO MONITOR!")


    def run(self):
        while self.running:
            self.listen_for_connections()
            while self.connected:
                try:
                    logging.warning(f"Sending heartbeat to monitor")
                    self.conn.send(bytes(self.name, 'utf-8'))
                    read = self.conn.recv(1024)
                    # if read == b'':
                    #     self.listen_for_connections()
                    logging.warning(f"Answer from server: {read.decode()}")
                    if self.name == "computers_category_filter_1":
                        logging.warning(f"Sleeping for 9 seconds")
                        time.sleep(9)
                    else:
                        time.sleep(1)
                        logging.warning(f"Sleeping for 1 second")
                except (socket.timeout, OSError) as e:
                    logging.error(f"Error in client: {e}")
                    self.conn.close()
                    self.connected = False
                    break


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
