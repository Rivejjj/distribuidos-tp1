import logging
import socket
from os import getenv
from multiprocessing import Process
from utils.initialize import initialize_config, initialize_log
from monitor import Monitor


def main():
    config_params = initialize_config([('port', True), ('host', True), ('logging_level', True)])
    config_params["port"] = int(config_params["port"])
    initialize_log(logging, config_params["logging_level"])
    
    # handle sigterm

    workers = ['computers_category_filter_0', 'computers_category_filter_1']
    monitor = Monitor(workers)
    monitor.run()
    


if __name__ == "__main__":
    main()
