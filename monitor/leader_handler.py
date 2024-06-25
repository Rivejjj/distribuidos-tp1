import logging
import socket
import time
import select

class LeaderHandler():
    def __init__(self,monitors,active_monitors,lock,name):
        self.monitors = monitors
        self.active_monitors = active_monitors
        self.lock = lock
        self.leader = None
        self.name = name
        self.running = True

    def find_and_delete(self,conn):
        for name,connection in self.active_monitors.items():
            if conn.getsockname() == connection.getsockname():
                del self.active_monitors[name]
                break

    def find_socket(self, conn):
        for connection in self.active_monitors.values():
            if conn.getsockname() == connection.getsockname():
                return connection
        return None

    def send_leader_message(self):
        with self.lock:
            for monitor, conn in self.active_monitors.items():
                try:
                    conn.send(bytes(self.name, 'utf-8'))
                    logging.warning(f"Sending leader message to {monitor}")
                except (ConnectionResetError, OSError) as e:
                    logging.warning(f"Connection to {monitor} lost: {e}")
                    self.find_and_delete(conn)
                    if len(self.active_monitors) == 0:
                        self.leader = (self.name,None)


    def check_connections(self):
        if self.leader[0] == self.name:
            with self.lock:
                readable, _, _ = select.select(self.active_monitors.values(), [], [], 1)
            for conn in readable:
                sock = self.find_socket(conn)
                if sock:
                    try:
                        data = conn.recv(1024)
                        logging.warning(f"Received heartbeat from {data}")
                        conn.send(b"Ok")
                    except (ConnectionResetError, OSError, BrokenPipeError) as e:
                        logging.warning(f"Connection to {data} lost: {e}")
                        with self.lock:
                            self.find_and_delete(conn)
                            logging.warning(f"active monitors: {self.active_monitors.keys()}")
                        
                else:
                    logging.warning(f"Connection not found")
        else:
            try:
                self.leader[1].send(bytes(self.name, 'utf-8'))
                logging.warning(f"Sending heartbeat to {self.leader[0]}")
                self.leader[1].recv(1024)
            except (ConnectionResetError, OSError) as e:
                logging.warning(f"Connection to {self.leader[0]} lost: {e}")
                self.get_leader()
            time.sleep(1)

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
                    sock.settimeout(10)
                    data = sock.recv(1024)
                    if data and data not in self.active_monitors:
                        with self.lock:
                            logging.warning(f"active monitors: {self.active_monitors}")
                            self.active_monitors[monitor] = sock
                            logging.warning(f"Received connection from: {monitor}")
                            if len(self.active_monitors) == len(self.monitors):
                                logging.warning(f"Connected with all monitors")
                                return
                    else:
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

    def run(self):
        logging.warning(f"starting leader handler ")
        self.connect_with_monitors()
        self.get_leader()
        while self.running:
            self.check_connections()