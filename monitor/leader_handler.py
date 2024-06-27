import logging
import socket
import time
import select
import signal
from multiprocessing import Process
from utils.sockets import receive, send_message
from utils.initialize import decode
from utils.revive import revive
from monitor import Monitor


TIME_BETWEEN_HEARTBEATS = 2
MAX_HEARTBEAT_TIMEOUT = 3 * TIME_BETWEEN_HEARTBEATS + 1


class LeaderHandler():
    def __init__(self, monitors, active_monitors, lock, name, highest_id, workers):
        signal.signal(signal.SIGTERM, lambda signal, frame: self.stop())
        self.highest_id = highest_id
        self.monitors = monitors
        self.active_monitors = active_monitors  # {monitor:conn}
        self.lock = lock
        self.leader = None  # (name sock)
        self.leader_hearbeat = None
        self.name = name
        self.running = True
        self.revived_monitors = set()
        self.heartbeats = {}
        self.workers_handler = None
        self.workers = workers

    def find_and_delete(self, conn):
        name, connection = self.find_socket(conn)
        logging.warning(f"Finding and deleting {name}")
        if connection and name in self.active_monitors:
            logging.warning(f"Deleting {name}")
            del self.active_monitors[name]
            logging.warning(
                f"active monitors: {self.active_monitors.keys()}")
            if name == self.leader[0]:
                self.leader = (None, None)
            return
        logging.warning(f"Connection not found")

    def find_socket(self, conn):
        with self.lock:
            for name, connection in self.active_monitors.items():
                if conn.getsockname() == connection.getsockname():
                    return name, connection
        logging.warning(f"Connection not found")
        return None, None

    def send_heartbeat(self):
        if self.leader:
            try:
                send_message(self.leader[1], self.name)
                logging.warning(f"Sending heartbeat to {self.leader[0]}")
            except (ConnectionResetError, OSError) as e:
                logging.warning(f"Could not send to {self.leader[0]} lost: {e}")
                self.get_leader()
            try:
                self.leader[1].setblocking(True)
                self.leader[1].settimeout(MAX_HEARTBEAT_TIMEOUT)
                decode(receive(self.leader[1]))
            except (ConnectionResetError, OSError, EOFError, socket.timeout) as e:
                logging.warning(f"Connection to {self.leader[0]} lost: {e}")
                self.leader = None
                self.get_leader()
                return
        else:
            self.get_leader()
        time.sleep(1)

    def autoproclaim_leader(self):
        logging.warning(f"I am leader")
        self.leader = (self.name, None)
        if not self.workers_handler:
            self.start_workers()

    def send_election_message(self):
        with self.lock:
            for name,conn in self.active_monitors.items():
                try:
                    conn.setblocking(True)
                    conn.settimeout(1)
                    receive(conn)
                except (ConnectionResetError, OSError, EOFError, socket.timeout) as e:
                    logging.warning(f"Connection to {name} lost in send election: {e}")
                    self.find_and_delete(conn)
            if len(self.active_monitors) == 0:
                logging.warning("No monitors connected in send election")
                self.autoproclaim_leader()
                return
            messages_sent = 0

            msg = "election"
            for name, conn in self.active_monitors.items():
                conn.setblocking(True)
                conn.settimeout(5)
                if name[-1] > self.name[-1]:
                    try:
                        logging.warning(f"Sending election message to {name}")
                        send_message(conn, msg)
                        messages_sent += 1
                    except (ConnectionResetError, OSError, socket.timeout) as e:
                        logging.warning(f"Connection to {name} lost: {e}")
                        self.find_and_delete(conn)
        if messages_sent == 0:
            self.autoproclaim_leader()
        while not self.leader:
            self.wait_for_answer()

    def wait_for_answer(self):
        logging.warning(f"Waiting for answer")
        with self.lock:
            values = self.active_monitors.values()
        try:
            readable, _, _ = select.select(
                list(values), [], [], 5)
        except (OSError, ValueError) as e:
            logging.warning(f"Error selecting: {e}")
            return
        if len(readable) == 0:
            logging.warning(f"Timeout polling. I am leader")
            self.send_coordinator_msg()
        for conn in readable:
            conn.setblocking(True)
            try:
                data = decode(receive(conn))
                if data and data.startswith("coordinator"):
                    self.handle_coordinator_message(conn, data)
                if data and data.startswith("monitor"):
                    logging.warning(f"Received heartbeat from {data}")
                    send_message(conn, "Ok")
                elif data and data.startswith("election"):
                    msg = "answer" + self.name
                    send_message(conn, msg)
                    return
            except socket.timeout:
                logging.warning(f"Timeout waiting for leader. I am leader")
                self.send_coordinator_msg()
            except (ConnectionResetError, OSError, EOFError) as e:
                logging.warning(f"Connection lost: {e}")
                with self.lock:
                    self.find_and_delete(conn)

    def handle_election_message(self, conn):
        self.leader = None
        if self.highest_id:
            self.send_coordinator_msg()
            return
        logging.warning(f"Handling election message")
        msg = "answer"
        try:
            send_message(conn, msg)
        except (ConnectionResetError, OSError) as e:
            logging.warning(f"Connection lost: {e}")
            self.find_and_delete(conn)
        self.send_election_message()
        while not self.leader:
            self.wait_for_answer()

    def handle_coordinator_message(self, conn, data):
        logging.warning(f"Handling coordinator message: {data}")
        msg = data.split(":")
        leader = msg[1]
        if leader[-1] > self.name[-1]:
            if self.workers_handler:
                self.workers_handler.terminate()
            self.leader = (leader, conn)
            logging.warning(f"New leader: {self.leader[0]}")

    def handle_message(self, conn, name, data):
        if data == "":
            logging.warning(f"Connection to {name} lost: empty message")
            self.find_and_delete(conn)
        elif data.startswith("monitor"):
            self.heartbeats[name] = time.time()
            logging.warning(f"Received heartbeat from {data}")
            send_message(conn, "Ok")
        elif data.startswith("election"):
            self.handle_election_message(conn)
        elif data.startswith("coordinator"):
            self.handle_coordinator_message(conn, data)
        elif data.startswith("answer"):
            logging.warning(f"Received answer")
        return

    def read_from_socket(self, conn, name):
        try:
            logging.warning(f"Reading from {name}")
            conn.setblocking(True)
            conn.settimeout(5)
            data = decode(receive(conn))
            self.handle_message(conn, name, data)
        except socket.timeout:
            logging.warning(f"Timeout reading from {name}")
            return
        except (ConnectionResetError, OSError, BrokenPipeError, EOFError) as e:
            logging.warning(f"Connection to {name} lost while reading: {e}")
            self.find_and_delete(conn)
            logging.warning(
                    f"active monitors: {self.active_monitors.keys()}")
            return

    def check_heartbeats(self):
        items = self.heartbeats.items()
        deleted_names = []
        for name, timestamp in items:
            if time.time() - timestamp > MAX_HEARTBEAT_TIMEOUT:
                logging.warning(f"Lost heartbeat from {name}")
                connections = list(self.active_monitors.values())
                for conn in connections:
                    self.find_and_delete(conn)
                deleted_names.append(name)

        for name in deleted_names:
            del self.heartbeats[name]

    def check_connections(self):
        while self.running:
            with self.lock:
                try:
                    readable, _, _ = select.select(
                        list(self.active_monitors.values()), [], [], TIME_BETWEEN_HEARTBEATS)
                except OSError as e:
                    logging.warning(f"Error selecting: {e}")
                    return
            for conn in readable:
                name, sock = self.find_socket(conn)
                if sock:
                    self.read_from_socket(conn, name)
                else:
                    logging.warning(f"Connection not found")

            if self.leader and self.leader[0] != self.name:
                self.send_heartbeat()
                return

            if self.leader and self.leader[0] == self.name:
                self.revive_monitors()
                self.check_heartbeats()
                return

    def revive_monitors(self):
        with self.lock:
            for monitor in self.monitors:
                if monitor not in self.active_monitors and monitor not in self.revived_monitors:
                    revive(monitor)
                    self.revived_monitors.add(monitor)
            for monitor in self.active_monitors.keys():
                if monitor in self.revived_monitors:
                    self.revived_monitors.remove(monitor)

    
    def send_coordinator_msg(self):
        self.leader = (self.name, None)
        with self.lock:
            for conn in self.active_monitors.values():
                msg = "coordinator:" + self.name
                send_message(conn, msg)
        if not self.workers_handler:
            self.start_workers()

    def get_leader(self):
        logging.warning(f"HIGHEST ID: {self.highest_id}")
        if self.highest_id:
            self.send_coordinator_msg()
            return
        logging.warning(f"Getting leader")
        self.send_election_message()

    def start_workers(self):
        self.workers_handler = Process(
            target=run_monitor, args=(self.workers,))
        self.workers_handler.daemon = True
        self.workers_handler.start()

    def run(self):
        logging.warning(f"starting leader handler ")
        self.connect_with_monitors()
        self.get_leader()
        while self.running:
            self.check_connections()
        logging.warning(f"Leader handler stopped")

    def stop(self):
        logging.warning(f"Stopping leader handler")
        self.running = False
        if self.workers_handler:
            self.workers_handler.terminate()
        with self.lock:
            for conn in self.active_monitors.values():
                conn.close()

    def connect_with_monitors(self):
        tries = 5
        while tries > 0:
            for monitor in self.monitors:
                with self.lock:
                    if monitor in self.active_monitors:
                        continue
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        sock.connect((monitor, 22226))
                    except (socket.timeout, OSError) as e:
                        logging.warning(
                            f"Error connecting with {monitor}: {e}")
                        sock.close()
                        continue
                    send_message(sock, self.name)
                    sock.settimeout(10)
                    try:
                        name = decode(receive(sock))
                    except (ConnectionResetError, OSError, EOFError, socket.timeout) as e:
                        logging.warning(
                            f"Error connecting with {monitor}: {e}")
                        sock.close()
                        continue
                    with self.lock:
                        if name and name not in self.active_monitors:
                            self.active_monitors[monitor] = sock
                            logging.warning(
                                f"Connected with: {monitor}")
                            if len(self.active_monitors) == len(self.monitors):
                                logging.warning(
                                    f"Connected with all monitors: {self.active_monitors.keys()}")
                                return
                        else:
                            logging.warning(f"NOT DATA: {monitor}")
                        if name in self.revived_monitors:
                            self.revived_monitors.remove(name)
                        sock.close()
                except (ConnectionRefusedError, EOFError, socket.gaierror) as e:
                    logging.warning(f"Error connecting with {monitor}: {e}")
            tries -= 1
            time.sleep(1)

def run_monitor(workers):
    monitor = Monitor(workers)
    monitor.run()