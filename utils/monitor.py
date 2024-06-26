import logging
from multiprocessing import Process
from monitor.monitor_client import MonitorClient


def send_heartbeat(name):
    logging.warning(f"Starting monitor client with name {name}")
    monitor_client = MonitorClient(name)
    monitor_client.run()


def start_monitor_process(name):
    process = Process(target=send_heartbeat, args=(name,))
    process.daemon = True
    process.start()
    return process
