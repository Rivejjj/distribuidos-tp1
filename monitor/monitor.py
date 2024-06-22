import logging 
from os import getenv
import subprocess
import time 
import socket

HEALTH_CHECK_INTERVAL = 3
MAX_HEARTBEAT_TIME = 3 * HEALTH_CHECK_INTERVAL + 1

class Monitor:
    def __init__(self, workers):
        self.last_heartbeat = {}
        self.running = True
        self.workers = workers
        self.active_workers = {}
        self.failed_connections = []

    def delete_node(self, node):
        logging.warning(f"Connection to {node} lost.")
        if node in self.active_workers:
            self.active_workers[node].close()
            del self.active_workers[node]
            self.failed_connections.append(node)

    def check_health(self):
        for worker in self.active_workers:
            try:
                data = self.active_workers[worker].recv(1024)
                if data and data != b"":
                    self.last_heartbeat[worker] = time.time()
                    self.active_workers[worker].send(b"Ok")
                else:
                    self.delete_node(worker)
                if time.time() - self.last_heartbeat[worker] > MAX_HEARTBEAT_TIME:
                    logging.warning(f"Connection to {worker} lost.")
                    self.delete_node(worker)
                    continue
            except (BrokenPipeError, OSError):
                logging.warning(f"Connection to {worker} lost.")
                self.delete_node(worker)

    def connect_to_worker(self,worker):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((worker, 22225))
            self.active_workers[worker] = sock
            logging.warning(f"Connected to {worker}")
            return True
        except (ConnectionRefusedError, socket.timeout) as e:
            self.failed_connections.append(worker)
            logging.warning(f"Error connecting with {worker}: {e}")
            return False
        
    def check_failed_connections(self):
        logging.warning(f"Checking failed connections: {self.failed_connections}")
        for worker in self.failed_connections:
            connected = self.connect_to_worker(worker)
            if connected:
                self.failed_connections.remove(worker)

    def establish_connections(self):
        for worker in self.workers:
            if worker in self.active_workers:
                continue
            self.connect_to_worker(worker)

    def run(self):
        logging.warning("Starting monitor")
        self.establish_connections()

        while self.running:
            self.check_failed_connections()
            self.check_health()
            time.sleep(1)
        
    def revive_node(self, node):
        result = subprocess.run(['/revive.sh',node],
                                check=False, 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        logging.warning('Command executed. Result={}\n. Output={}\n. Error={}\n'.
            format(result.returncode, result.stdout, result.stderr))


