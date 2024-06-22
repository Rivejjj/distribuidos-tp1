import logging 
import signal
import subprocess
import time 
import socket
import select 

HEALTH_CHECK_INTERVAL = 3
MAX_HEARTBEAT_TIME = 3 * HEALTH_CHECK_INTERVAL + 1

class Monitor:
    def __init__(self, workers):
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())
        self.last_heartbeat = {}
        self.running = True
        self.workers = workers
        self.active_workers = {}
        self.failed_workers = []
        self.restarted_workers = []

    def delete_node(self, node):
        logging.warning(f"Connection to {node} lost.")
        if node in self.active_workers:
            self.active_workers[node].close()
            del self.active_workers[node]
        if node not in self.restarted_workers:
            self.failed_workers.append(node)

    def check_health(self):
        ready_to_read, _, _ = select.select(self.active_workers.values(), [], [], MAX_HEARTBEAT_TIME)
        workers = list(self.active_workers.keys())
        for worker in workers:
            try:
                data = self.active_workers[worker].recv(1024)
                if data and data != b"":
                    self.last_heartbeat[worker] = time.time()
                    self.active_workers[worker].send(b"Ok")
                else:
                    self.delete_node(worker)
                if time.time() - self.last_heartbeat[worker] > MAX_HEARTBEAT_TIME:
                    logging.warning(f"Connection to {worker} lost due to inactivity.")
                    self.delete_node(worker)
                    continue
            except (BrokenPipeError, OSError) as e:
                logging.warning(f"Connection to {worker} lost: {e}")
                self.delete_node(worker)

    def connect_to_worker(self,worker):
        logging.warning(f"Trying to connect with: {worker}")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((worker, 22225))
            self.active_workers[worker] = sock
            if worker in self.restarted_workers:
                self.restarted_workers.remove(worker)
            logging.warning(f"Connected to {worker}")
        except (ConnectionRefusedError, socket.timeout) as e:
            if worker not in self.restarted_workers:
                self.failed_workers.append(worker)
            logging.warning(f"Error connecting with {worker}: {e}")
        
    def check_failed_workers(self):
        logging.warning(f"Checking failed connections: {self.failed_workers}")

        failed_conns = list(self.failed_workers)
        for worker in failed_conns:
            if worker not in self.restarted_workers:
                self.revive_node(worker)
                self.failed_workers.remove(worker)
                self.restarted_workers.append(worker)

        for worker in self.restarted_workers:
            self.connect_to_worker(worker)

    def establish_connections(self):
        for worker in self.workers:
            if worker in self.active_workers:
                continue
            self.connect_to_worker(worker)

    def run(self):
        logging.warning("Starting monitor")
        self.establish_connections()

        while self.running:
            self.check_failed_workers()
            self.check_health()
        
    def revive_node(self, node):
        result = subprocess.run(['/revive.sh',node],
                                check=False, 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        logging.warning('Command executed. Result={}\n. Output={}\n. Error={}\n'.
        format(result.returncode, result.stdout, result.stderr))

    def stop(self):
        self.running = False
        for worker in self.active_workers:
            self.active_workers[worker].close()

