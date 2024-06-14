import socket
import logging
import time

class MonitorClient():
    def __init__(self, address, port, name):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.address = address
        self.port = port
        self.name = name

    def connect(self):
        while not self.connected:
            try:
                self.sock.connect((self.address, self.port))
                self.connected = True
                logging.warning(f"Connected to monitor")
            except ConnectionRefusedError:
                logging.warning(f"Connection refused. Retrying in 1 seconds")
                self.connected = False
                time.sleep(1)
            except socket.gaierror:
                logging.warning(f"Host name invalid. Monitor not alive. Retrying in 1 seconds")
                self.connected = False
                time.sleep(1)

    def run(self):
        self.connect()
        while self.connected:
            try:    
                logging.warning(f"Sending heartbeat to monitor")
                self.sock.send(bytes(self.name, 'utf-8'))
                read = self.sock.recv(1024)
                logging.warning(f"Answer from server: {read.decode()}")
                time.sleep(3)
            except:
                logging.error("Error while sending heartbeat")
                break

    def send(self, data):
        self.socket.sendall(data)

    def close(self):
        self.socket.close()