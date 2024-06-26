import logging
import socket
import time
import select
import errno
from utils.sockets import receive, send_message
from utils.initialize import decode

TIME_BETWEEN_HEARTBEATS = 2

class LeaderHandler():
    def __init__(self,monitors,active_monitors,lock,name,highest_id):
        self.highest_id = highest_id
        self.monitors = monitors
        self.active_monitors = active_monitors # {monitor:conn}
        self.lock = lock
        self.leader = None #(name sock)
        self.name = name
        self.running = True

    def find_and_delete(self,conn):
        name,connection = self.find_socket(conn)
        logging.warning(f"Finding and deleting {name}")
        with self.lock:
            if connection and name in self.active_monitors:
                logging.warning(f"Deleting {name}")
                del self.active_monitors[name]
                logging.warning(f"active monitors: {self.active_monitors.keys()}")
                return
        logging.warning(f"Connection not found")
        

    def find_socket(self, conn):
        with self.lock:
            for name,connection in self.active_monitors.items():
                if conn.getsockname() == connection.getsockname():
                    return name,connection
        logging.warning(f"Connection not found")
        return None, None

    def send_heartbeat(self):
        try:
            send_message(self.leader[1], self.name)
            logging.warning(f"Sending heartbeat to {self.leader[0]}")
        except (ConnectionResetError, OSError) as e:
            logging.warning(f"Could not send to {self.leader[0]} lost: {e}")
            self.get_leader()
        try:
            self.leader[1].setblocking(True)
            data = decode(receive(self.leader[1]))
            #actualize timestamp
        except (ConnectionResetError, OSError, EOFError) as e:
            logging.warning(f"Connection to {self.leader[0]} lost: {e}")
            self.leader = None
            self.get_leader()
        time.sleep(1)

    def send_election_message(self):
        with self.lock:
            msg = "election" 
            for name,conn in self.active_monitors.items():
                if name[-1] > self.name[-1]:
                    try:
                        logging.warning(f"Sending election message to {name}")
                        send_message(conn, msg)
                    except (ConnectionResetError, OSError) as e:
                        logging.warning(f"Connection to {name} lost: {e}")
                        self.find_and_delete(conn)

    def wait_for_answer(self):
        logging.warning(f"Waiting for answer")

        readable, _, _ = select.select(list(self.active_monitors.values()), [], [], 5)
        if not readable:
            logging.warning(f"Timeout polling. I am leader")
            self.send_coordinator_msg()
        for conn in readable:
            conn.setblocking(True)
            try:
                data = decode(receive(conn))
                if data and data.startswith("coordinator"):
                    self.handle_coordinator_message(conn,data)
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
                self.find_and_delete(conn)

    def handle_election_message(self,conn):
        self.leader = None
        if self.highest_id:
            self.send_coordinator_msg()
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

    def handle_coordinator_message(self,conn,data):
        logging.warning(f"Handling coordinator message: {data}")
        msg = data.split(":")
        leader = msg[1]
        if leader[-1] > self.name[-1]:
            self.leader = (leader,conn)
            logging.warning(f"New leader: {self.leader[0]}")
        else:
            self.send_election_message()

    def handle_message(self,conn,name,data):
        if data == "":
            logging.warning(f"Connection to {name} lost")
            self.find_and_delete(conn)
        elif data.startswith("monitor"):
            logging.warning(f"Received heartbeat from {data}")
            send_message(conn, "Ok")
        elif data.startswith("election"):
            self.handle_election_message(conn)
        elif data.startswith("coordinator"):
            self.handle_coordinator_message(conn,data)
        elif data.startswith("answer"):
            logging.warning(f"Received answer")
            return

    def read_from_socket(self,conn,name):
        try:
            logging.warning(f"Reading from {name}")
            conn.setblocking(True)
            conn.settimeout(5)
            data = decode(receive(conn))
            self.handle_message(conn,name,data)
        except socket.timeout:
            logging.warning(f"Timeout reading from {name}")
            return
        except (ConnectionResetError, OSError, BrokenPipeError, EOFError) as e:
            logging.warning(f"Connection to {name} lost: {e}")
            self.find_and_delete(conn)
            logging.warning(f"active monitors: {self.active_monitors.keys()}")

    def check_connections(self):
        with self.lock:
            if len(self.active_monitors) == 0:
                logging.warning(f"No active monitors")
                time.sleep(1)
                return
            try:
                readable, _, _ = select.select(list(self.active_monitors.values()), [], [], TIME_BETWEEN_HEARTBEATS)
            except Exception as e:
                logging.warning(f"Error selecting: {e}")
                return
        for conn in readable:
            name, sock = self.find_socket(conn)
            if sock:
                self.read_from_socket(conn,name)
            else:
                logging.warning(f"Connection not found")
        
        if self.leader and self.leader[0] != self.name:
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
                    send_message(sock, self.name)
                    sock.settimeout(5)
                    data = decode(receive(sock))
                    if data and data not in self.active_monitors:
                        with self.lock:
                            self.active_monitors[monitor] = sock
                            logging.warning(f"Received connection from: {monitor}")
                            if len(self.active_monitors) == len(self.monitors):
                                logging.warning(f"Connected with all monitors: {self.active_monitors.keys()}")
                                return
                    else:
                        logging.warning(f"NOT DATA: {monitor}")
                        sock.close()
                except (ConnectionRefusedError, EOFError, socket.gaierror) as e:
                    logging.warning(f"Error connecting with {monitor}: {e}")
            tries -= 1
            time.sleep(1)

    def send_coordinator_msg(self):
        self.leader = (self.name,None)
        with self.lock:
            for conn in self.active_monitors.values():
                msg = "coordinator:" + self.name
                send_message(conn, msg)

    def get_leader(self):
        if self.highest_id:
            self.send_coordinator_msg()
            return
        logging.warning(f"Getting leader")
        self.send_election_message()
        

    def run(self):
        logging.warning(f"starting leader handler ")
        self.connect_with_monitors()
        self.get_leader()
        while self.running:
            self.check_connections()