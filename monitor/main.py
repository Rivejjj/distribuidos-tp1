import logging
import socket
from multiprocessing import Process
from utils.initialize import initialize_config, initialize_log
from monitor import Monitor

def handle_connection(conn, addr):
    monitor = Monitor(conn,addr)
    monitor.run()
        
def listen_for_connections(sock):
    conn, addr = sock.accept()
    logging.warning(f"NEW CONNECTION !!!!!!!!!!!!!!")
    return conn, addr


def main():
    config_params = initialize_config([('port', True), ('host', True), ('logging_level', True)])
    config_params["port"] = int(config_params["port"])
    initialize_log(logging, config_params["logging_level"])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', config_params["port"]))
    sock.listen()
    logging.warning(f"Listening")

    # handle sigterm

    while True:
        conn, addr = listen_for_connections(sock)
        if conn:
            process = Process(target=handle_connection, args=(conn,addr))
            process.start()


if __name__ == "__main__":
    main()
