import logging
import socket
import time
import select
import errno

class LeaderHandler():
    def __init__(self,monitors,active_monitors,lock,name):
        self.monitors = monitors
        self.active_monitors = active_monitors # {monitor:conn}
        self.lock = lock
        self.leader = None #name sock
        self.name = name
        self.running = True

    def find_and_delete(self,conn):
        logging.warning(f"Finding and deleting {conn}")
        name,connection = self.find_socket(conn)
        logging.warning(f"Found {name} and {connection}")
        logging.warning(f"active monitors: {self.active_monitors.keys()}")
        with self.lock:

            if connection and name in self.active_monitors:
                logging.warning(f"Deleting {name}")
                del self.active_monitors[name]
                logging.warning(f"active monitors: {self.active_monitors.keys()}")
        

    def find_socket(self, conn):
        logging.warning(f"Finding {conn}")
        with self.lock:
            for name,connection in self.active_monitors.items():
                if conn.getsockname() == connection.getsockname():
                    return name,connection
            logging.warning(f"Connection not found")
            return None, None

    # def send_leader_message(self):
    #     with self.lock:
    #         for monitor, conn in self.active_monitors.items():
    #             try:
    #                 conn.send(bytes(self.name, 'utf-8'))
    #                 logging.warning(f"Sending leader message to {monitor}")
    #             except (ConnectionResetError, OSError) as e:
    #                 logging.warning(f"Connection to {monitor} lost: {e}")
    #                 self.find_and_delete(conn)
    #                 if len(self.active_monitors) == 0:
    #                     self.leader = (self.name,None)

    def send_heartbeat(self):
        try:
            self.leader[1].send(bytes(self.name, 'utf-8'))
            logging.warning(f"Sending heartbeat to {self.leader[0]}")
        except (ConnectionResetError, OSError) as e:
            logging.warning(f"Could not send to {self.leader[0]} lost: {e}")
            self.get_leader()
        try:
            logging.warning(f"waiting for answer from leader")
            self.leader[1].setblocking(True)
            self.leader[1].recv(1024)
            logging.warning(f"answer received from leader")
        except (ConnectionResetError, OSError) as e:
            if e.errno == errno.EWOULDBLOCK:
                logging.warning(f"Error reading [{self.leader[0]}]: {e}")
                time.sleep(1)
                return
            logging.warning(f"Connection to {self.leader[0]} lost: {e}")
            self.get_leader()
        time.sleep(1)

    def handle_leader_message():
        pass

    def handle_election_message():
        pass

    def handle_message(self,conn,name,data):
        if data == b"":
            logging.warning(f"Connection to {name} lost")
            self.find_and_delete(conn)
        if data.startswith("monitor"):
            logging.warning(f"Received heartbeat from {data}")
            conn.send(b"Ok")
        if data.startswith("election"):
            self.handle_election_message()
        if data.startswith("leader"):
            msg = data.split(":")
            leader = msg[1]

    def read_from_socket(self,conn,name):
        try:
            logging.warning(f"Reading from {name}")
            data = conn.recv(1024)
            
        except socket.timeout:
            logging.warning(f"Timeout reading from {name}")
            return
        except (ConnectionResetError, OSError, BrokenPipeError) as e:
            logging.warning(f"Connection to {name} lost: {e}")
            with self.lock:
                self.find_and_delete(conn)
                logging.warning(f"active monitors: {self.active_monitors.keys()}")

    def check_connections(self):
        if self.leader[0] == self.name:
            with self.lock:
                if len(self.active_monitors) == 0:
                    logging.warning(f"No active monitors")
                    time.sleep(1)
                    return
                try:
                    readable, _, _ = select.select(list(self.active_monitors.values()), [], [], 1)
                except Exception as e:
                    logging.warning(f"Error selecting: {e}")
                    return
            for conn in readable:
                name, sock = self.find_socket(conn)
                if sock:
                    self.read_from_socket(conn,name)
                else:
                    logging.warning(f"Connection not found")
        else:
            self.send_heartbeat()

    def connect_with_monitors(self):
        tries = 5
        while tries > 0 :
            for monitor in self.monitors:
                with self.lock:
                    if monitor in self.active_monitors:
                        continue
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((monitor, 22226))
                    sock.send(bytes(self.name, 'utf-8'))
                    sock.settimeout(5)
                    data = sock.recv(1024)
                    if data and data not in self.active_monitors:
                        with self.lock:
                            logging.warning(f"active monitors: {self.active_monitors}")
                            self.active_monitors[monitor] = sock
                            logging.warning(f"Received connection from: {monitor}")
                            if len(self.active_monitors) == len(self.monitors):
                                logging.warning(f"Connected with all monitors: {self.active_monitors.keys()}")
                                return
                    else:
                        logging.warning(f"NOT DATA: {monitor}")
                        sock.close()
                except ConnectionRefusedError as e:
                    logging.warning(f"Error connecting with {monitor}: {e}")
            tries -= 1
            time.sleep(1)

    def get_leader(self):
        logging.warning(f"Getting leader")
        self.leader = (self.name,None)
        max_id = self.name[-1]
        with self.lock:
            for monitor, conn in self.active_monitors.items():
                if monitor[-1] > max_id:
                    self.leader = (monitor,conn)
                    max_id = monitor[-1]
        logging.warning(f"Leader is {self.leader[0]}, with conn {self.leader[1]}")

    def run(self):
        logging.warning(f"starting leader handler ")
        self.connect_with_monitors()
        self.get_leader()
        while self.running:
            self.check_connections()