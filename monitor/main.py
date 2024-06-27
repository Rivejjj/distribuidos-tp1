import logging
import socket
import signal
from multiprocessing import Process, Manager
from utils.initialize import initialize_config, initialize_log
from utils.sockets import send_message, receive
from monitor import Monitor
from leader_handler import LeaderHandler


def run_monitor(workers):
    monitor = Monitor(workers)
    monitor.run()


def listen_for_connections(running, sock, lock, active_monitors):
    while running:
        conn, addr = sock.accept()
        data = receive(conn)
        if data:
            logging.warning(f"Received connection from: {data.decode()}")
            monitor_name = data.decode()
            send_message(conn, "Ok")
            with lock:
                if monitor_name not in active_monitors:
                    active_monitors[monitor_name] = conn
                    logging.warning(
                        f"ACA falla active monitors: {active_monitors.keys()}")
        else:
            conn.close()
            logging.warning(f"Connection closed")


def signal_handler(sig, frame):
    logging.warning("Received SIGTERM")
    sock.close()
    process.terminate()
    leader_handler.stop()


if __name__ == "__main__":
    config_params = initialize_config(
        [('port', True), ('host', True), ('logging_level', True), ('name', True), ('workers', True), ('highest_id', True)])
    config_params["port"] = int(config_params["port"])
    initialize_log(logging, config_params["logging_level"])

    monitors = ['monitor0', 'monitor1', 'monitor2']
    if config_params["name"] in monitors:
        monitors.remove(config_params["name"])

    manager = Manager()
    lock = manager.Lock()
    active_monitors = manager.dict()  # {monitor_name: socket}

    running = True
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 22226))
    sock.listen()

    process = Process(target=listen_for_connections, args=(
        running, sock, lock, active_monitors))
    process.daemon = True
    process.start()

    config_params["workers"] = config_params["workers"].split(',')
    workers = config_params["workers"]

    if config_params["name"] == "monitor2":
        leader_handler = LeaderHandler(
            monitors, active_monitors, lock, config_params["name"], True, workers)
    else:
        leader_handler = LeaderHandler(
            monitors, active_monitors, lock, config_params["name"], False, workers)

    # handle sigterm
    signal.signal(signal.SIGTERM, lambda signal,
                  frame: signal_handler(process, leader_handler))

    leader_handler.run()
