import logging 
import subprocess
import time 


class Monitor:
    def __init__(self,conn,addr):
        self.conn = conn
        self.addr = addr
        self.name = None
        self.last_heartbeat = None
        self.running = True


    def add_node(self):
        try:
            data = self.conn.recv(1024)
            if data:
                self.name = data.decode()
                self.conn.send(b"OK")
                self.last_heartbeat = time.time()
        except BrokenPipeError:
            logging.warning("[SERVER] broken pipe")

    def check_health(self):
        try:
            data = self.conn.recv(1024)
            if not data:
                self.revive_node(self.name)
                self.stop()
            logging.warning(f"Received data: {data.decode()}")
            self.last_heartbeat = time.time()
            self.conn.send(b"OK")

        except BrokenPipeError:
            logging.warning("[SERVER] broken pipe")
            self.revive_node(self.name)
            self.stop()

        except OSError:
            logging.warning("[SERVER] bad file descriptor")
            self.stop()


    def revive_node(self, node):
        result = subprocess.run(['/revive.sh',node],
                                check=False, 
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        logging.warning('Command executed. Result={}\n. Output={}\n. Error={}\n'.
            format(result.returncode, result.stdout, result.stderr))

    def run(self):
        self.add_node()
        while self.running:
            self.check_health()
            time.sleep(3)

    def stop(self):
        self.running = False
        self.conn.close()
        logging.warning(f"Connection closed with {self.addr}")