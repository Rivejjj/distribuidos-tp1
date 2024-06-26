import logging
import socket
from multiprocessing import Process, Manager
from utils.initialize import initialize_config, initialize_log
from utils.sockets import send_message, receive
from monitor import Monitor
from leader_handler import LeaderHandler

def run_monitor(workers):
    monitor = Monitor(workers)
    monitor.run()

def handle_leader(monitors,active_monitros,lock,config_params):
    if config_params["name"] == "monitor2":
        leader_handler = LeaderHandler(monitors,active_monitros,lock,config_params["name"], True)
    else:
        leader_handler = LeaderHandler(monitors,active_monitros,lock,config_params["name"], False)
    leader_handler.run()


if __name__ == "__main__":
    config_params = initialize_config([('port', True), ('host', True), ('logging_level', True), ('name', True)])
    config_params["port"] = int(config_params["port"])
    initialize_log(logging, config_params["logging_level"])
    
    # handle sigterm
    
    # workers = ['computers_category_filter_0',
    #             'computers_category_filter_1',
    #             'computers_category_filter_2',
    #             '2000s_published_year_filter_0',
    #             '2000s_published_year_filter_1',
    #             '2000s_published_year_filter_2',
    #             'title_contains_filter_0',
    #             'title_contains_filter_1',
    #             'title_contains_filter_2',
    #             'decades_accumulator_0',
    #             'decades_accumulator_1',
    #             'decades_accumulator_2',
    #             '1990s_published_year_filter_0',
    #             '1990s_published_year_filter_1',
    #             '1990s_published_year_filter_2',
    #             'reviews_counter_0',
    #             'reviews_counter_1',
    #             'reviews_counter_2',
    #             'avg_rating_accumulator',
    #             'fiction_category_filter_0',
    #             'fiction_category_filter_1',
    #             'fiction_category_filter_2',
    #             'sentiment_analyzer_0',
    #             'sentiment_analyzer_1',
    #             'sentiment_analyzer_2',
    #             'sentiment_score_accumulator'
                # ]

    # process = Process(target=run_monitor, args=(workers,))
    # process.daemon = True
    # process.start()

    

    monitors = ['monitor0','monitor1', 'monitor2']
    if config_params["name"] in monitors:
        monitors.remove(config_params["name"])

    manager = Manager()
    lock = manager.Lock()
    active_monitors = manager.dict() # {monitor_name: socket}

    process = Process(target=handle_leader, args=(monitors,active_monitors,lock,config_params))
    process.daemon = True
    process.start()

    running = True
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 22226))
    sock.listen()

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
                    logging.warning(f"active monitors: {active_monitors.keys()}")
        else:
            conn.close()
            logging.warning(f"Connection closed")
    

    
    