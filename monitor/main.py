import logging
import socket
import time
import threading
import select
from os import getenv
from multiprocessing import Process, Lock, Manager
from utils.initialize import initialize_config, initialize_log
from monitor import Monitor
from leader_handler import LeaderHandler

def run_monitor(workers):
    monitor = Monitor(workers)
    monitor.run()

def listen_for_connections(lock, active_monitors):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 22226))
    sock.listen()
    running = True
    while running:
        connection, client_address = sock.accept()
        lock.acquire()
        try:
            data = connection.recv(1024).decode()
            logging.warning(f'RECEIVED connection from {data}')
            connection.send(b"Ok")
            
            logging.warning(f"active monitors: {active_monitors.keys()}, data: {data}, {data in list(active_monitors.keys())}")
            if data not in list(active_monitors.keys()):
                active_monitors[data] = connection
                logging.warning(f"THE SOCKET STORED IS: {sock}")
            else:
                logging.warning(f"already connected to {data}")
                connection.close()
            logging.warning(f"active monitors: {active_monitors.keys()}")
        except Exception as e:
            logging.error(f'error la concha de la lora {e}')
            pass
        lock.release()


if __name__ == "__main__":
    config_params = initialize_config([('port', True), ('host', True), ('logging_level', True), ('name', True)])
    config_params["port"] = int(config_params["port"])
    initialize_log(logging, config_params["logging_level"])
    
    # handle sigterm

    monitors = ['monitor0','monitor1', 'monitor2']
    if config_params["name"] in monitors:
        monitors.remove(config_params["name"])

    manager = Manager()
    lock = manager.Lock()
    active_monitors = manager.dict() # {monitor_name: socket}

    process = Process(target=listen_for_connections, args=(lock,active_monitors))
    process.daemon = True
    process.start()

    leader_handler = LeaderHandler(monitors, config_params["name"], lock, active_monitors)
    leader_handler.connect_with_monitors()
    logging.warning(f"active monitors: {active_monitors}")

    leader_handler.elect_leader()

    leader_handler.run()



    

    
    # workers = ['computers_category_filter_0',
    #             'computers_category_filter_1',
    #             'computers_category_filter_2',
    #             '2000s_published_year_filter_0',
    #             '2000s_published_year_filter_1',
    #             '2000s_published_year_filter_2']

    # process = Process(target=run_monitor, args=(workers,))
    # process.daemon = True
    # process.start()
    

