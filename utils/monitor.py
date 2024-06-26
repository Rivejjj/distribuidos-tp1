import logging
from multiprocessing import Process
import subprocess
from monitor_client import MonitorClient  # type: ignore


def send_heartbeat(name):
    logging.warning(f"Starting monitor client with name {name}")
    monitor_client = MonitorClient(name)
    monitor_client.run()


def revive(node):
    result = subprocess.run(['/revive.sh', node],
                            check=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    logging.warning('Command executed. Result={}\n. Output={}\n. Error={}\n'.
                    format(result.returncode, result.stdout, result.stderr))


def start_monitor_process(name):
    process = Process(target=send_heartbeat, args=(name,))
    process.daemon = True
    process.start()
    return process
