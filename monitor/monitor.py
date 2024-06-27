import logging
import signal
import subprocess
import time
import socket
import select
from utils.sockets import receive, send_message
from utils.revive import revive

HEALTH_CHECK_INTERVAL = 4
MAX_HEARTBEAT_TIME = 3 * HEALTH_CHECK_INTERVAL + 1


class Monitor:
    def __init__(self, workers):
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())
        self.last_heartbeat = {}
        self.running = True
        self.workers = workers
        self.active_workers = {}  # {socket: worker}
        self.failed_workers = []  # [worker]
        self.restarted_workers = []  # [worker]

    def delete_node(self, node):
        logging.warning(f"Connection to {node} lost.")
        name = self.active_workers[node]
        if node in self.active_workers:
            node.close()
            del self.active_workers[node]
        if name not in self.restarted_workers:
            self.failed_workers.append(name)


    def check_last_heartbeats(self):
        active_workers = list(self.active_workers.keys())
        for sock in active_workers:
            actual_time = time.time()
            if actual_time - self.last_heartbeat[sock] > MAX_HEARTBEAT_TIME:
                logging.warning(
                    f"[WORKER HANDLER] Connection to {self.active_workers[sock]} lost due to inactivity.")
                logging.warning(f"times: {actual_time} - {self.last_heartbeat[sock]} ={actual_time - self.last_heartbeat[sock]}")
                self.delete_node(sock)

    def check_health(self):
        # logging.warning(f"Checking health: available workers: {self.active_workers.values()} \nFailed workers: {self.failed_workers} \nRestarted workers: {self.restarted_workers}")
        try:
            ready_to_read, _, _ = select.select(
                self.active_workers.keys(), [], [], MAX_HEARTBEAT_TIME)
        except (OSError, ValueError) as e:
            logging.error(f"[WORKER HANDLER] Error in select: {e}")
            return
        for sock in ready_to_read:
            try:
                data = receive(sock)
                if data and data != b"":
                    self.last_heartbeat[sock] = time.time()
                    send_message(sock, "Ok")
                    logging.warning(
                        f"[WORKER HANDLER] Received heartbeat from {self.active_workers[sock]}")
                else:
                    self.delete_node(sock)
            except (BrokenPipeError, OSError, EOFError) as e:
                logging.warning(
                    f"[WORKER HANDLER] Connection to {self.active_workers[sock]} lost: {e}...")
                self.delete_node(sock)
        self.check_last_heartbeats()

    def connect_to_worker(self, worker):
        logging.warning(f"[WORKER HANDLER] Trying to connect with: {worker}")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((worker, 22225))
            sock.settimeout(10)
            self.active_workers[sock] = worker
            self.last_heartbeat[sock] = time.time()
            if worker in self.restarted_workers:
                self.restarted_workers.remove(worker)
            logging.warning(f"[WORKER HANDLER] Connected to {worker} and time: {self.last_heartbeat[sock]}")
            logging.warning(f"[WORKER HANDLER] Active workers: {self.active_workers.values()}")
        except (ConnectionRefusedError, socket.timeout) as e:
            logging.warning(f"[WORKER HANDLER] Error connecting with {worker}: {e}")
            if worker not in self.restarted_workers:
                self.failed_workers.append(worker)
        except socket.gaierror as e:
            logging.warning(f"[WORKER HANDLER] gaierror with {worker}: {e}")
            if worker not in self.failed_workers:
                self.failed_workers.append(worker)
            if worker in self.restarted_workers:
                logging.warning(f"[WORKER HANDLER] Removing {worker} from restarted workers")
                self.restarted_workers.remove(worker)
        except OSError as e:
            logging.error(f"[WORKER HANDLER] Error connecting with {worker}: {e}")
            self.connect_to_worker(worker)

    def check_failed_workers(self):
        failed_conns = list(self.failed_workers)
        for worker in failed_conns:
            if worker not in self.restarted_workers:
                revive(worker)
                self.failed_workers.remove(worker)
                self.restarted_workers.append(worker)

        for worker in self.restarted_workers:
            self.connect_to_worker(worker)

    def establish_connections(self):
        for worker in self.workers:
            if worker in self.active_workers.values():
                continue
            self.connect_to_worker(worker)

    def run(self):
        logging.warning("[WORKER HANDLER] Starting monitor")
        self.establish_connections()
        while self.running:
            self.check_failed_workers()
            self.check_health()
        logging.warning("[WORKER HANDLER] Monitor stopped")

    def stop(self):
        self.running = False
        for worker in self.active_workers:
            worker.close()
