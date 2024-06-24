import select
import logging
import socket
import time

class LeaderHandler():
    def __init__(self, monitors,name,lock, active_monitors):
        self.monitors = monitors
        self.active_monitors = active_monitors # {monitor: conn}
        self.leader = None
        self.lock = lock
        self.name = name

    def send_hearbeat(self):
        try:
            self.active_monitors[self.leader].send(self.name)
        except BrokenPipeError:
            self.leader = None
            self.active_monitors.pop(self.leader)
            self.elect_leader()

    def elect_leader(self):
        max_id = self.name[-1]
        self.leader = self.name
        for monitor in self.active_monitors:
            if monitor[-1] > max_id:
                max_id = monitor[-1]
                self.leader = monitor

    def add_monitor(self, monitor, conn):
        self.active_monitors[monitor] = conn

    def __find_monitor(self, conn):
        logging.warning(f"LOOKING FOR conn: {conn}")
        logging.warning(f"active monitors: {self.active_monitors}")
        for monitor, c in self.active_monitors.items():
            if c == conn:
                logging.warning(f"found monitor: {monitor}")
                return monitor
        logging.warning(f"monitor not found")
        return None

    def remove_monitor(self, conn):
        monitor = self.__find_monitor(conn)
        if monitor:
            conn.close()
            self.active_monitors.pop(monitor)


    def handle_message(self,conn, data):
        logging.warning(f"received message: {data}")
        if data == b"":
            self.remove_monitor(conn)
        else:
            try:
                conn.send(b"Ok")
            except (BrokenPipeError, ConnectionResetError) as e:
                logging.error(f"Error sending message: {e}")
                self.remove_monitor(conn)
            

    def check_monitors(self):
        try:
            readable, _, _ = select.select(self.active_monitors.values(), [], [], 1)
        except OSError as e:
            logging.error(f"Error in leader handler: {e}")

        for conn in readable:
            try:
                data = conn.recv(1024)
            except ConnectionResetError:
                self.remove_monitor(conn)
                continue

            self.handle_message(conn,data)

            

    def connect_with_monitors(self):
        tries = 5
        while tries > 0:
            if len(self.active_monitors) == len(self.monitors):
                break
            for mon in self.monitors:
                self.lock.acquire()
                if mon not in self.active_monitors.keys():
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(10.0)
                        sock.connect((mon, 22226))
                        sock.send(self.name.encode())
                        recv = sock.recv(1024)
                        if recv == b"Ok":
                            logging.warning(f"connected to {mon}: recv: {recv}")
                            self.active_monitors[mon] = sock
                            self.lock.release()
                            continue
                    except socket.gaierror as e:
                        logging.warning(f"could not connect to {mon}: {e}")
                        sock.close()
                        self.lock.release()
                        break
                    except ConnectionRefusedError as e:
                        logging.warning(f"could not connect to {mon}: {e}")
                        pass
                    self.lock.release()
                    tries -= 1
                else:
                    logging.warning(f"already connected to {mon}")
                    self.lock.release()
            time.sleep(1)
            tries -= 1
        
    def run(self):
        while True:
            if len(self.active_monitors) == 0:
                logging.error("I am the lone leader 8)")
                time.sleep(3)
                continue
            if self.name == self.leader:
                    self.check_monitors()
            else: 
            
                try:
                    self.active_monitors[self.leader].send(b"Hello im " + self.name.encode())
                    logging.warning(f"sent hello to leader: {self.leader}")
                except Exception as e:
                    logging.error(f"error sending hello to {self.leader}: {e}")
          
                    
            time.sleep(2)