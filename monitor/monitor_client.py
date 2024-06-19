import socket
import logging
import time

class MonitorClient():
    def __init__(self, name):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.connected = False
        self.address = None
        self.port = None
        self.name = name

    def connect(self, monitors):
        
        attempts = 5
        index = 0
        self.address, self.port = monitors[index]

        while not self.connected and attempts >= 0:
            attempts = self.check_attempts(attempts, index, monitors)
            try:
                self.sock.connect((self.address, self.port))
                self.connected = True
                logging.warning(f"Connected to monitor: {self.address} {self.port}")
            except ConnectionRefusedError:
                logging.warning(f"Connection refused with {self.address}. Retrying in 1 seconds")
                self.connected = False
                time.sleep(1)
            except socket.gaierror:
                logging.warning(f"Host name invalid: {self.address}. Monitor not alive. Retrying in 1 seconds")
                self.connected = False
                time.sleep(1)
            finally:
                tries_remaining -= 1

    def run(self):
        monitors = [("monitor2", 22223), ("monitor1", 22223), ("monitor0", 22223)]
        self.connect(monitors)
        while self.connected:
            try:    
                logging.warning(f"Sending heartbeat to monitor")
                self.sock.send(bytes(self.name, 'utf-8'))
                read = self.sock.recv(1024)
                if read == b'':
                    self.restart_connection()
                logging.warning(f"Answer from server: {read.decode()}")
                time.sleep(3)
            except (socket.timeout, OSError) as e:
                    logging.error(f"Error in client: {e}")
                    self.restart_connection()
    


    def restart_connection(self):
        logging.warning(f"Restarting connection")
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.address = None
        self.port = None
        self.connect()
        time.sleep(1)

    def check_attempts(self, attempts, index, monitors):
        if attempts == 0:
            index = (index + 1) % 3
            self.address, self.port = monitors[index]
            attempts = 5
        return attempts
    
    def close(self):
        self.connected = False
        self.sock.close()
