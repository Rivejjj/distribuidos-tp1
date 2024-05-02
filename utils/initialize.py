from configparser import ConfigParser
import logging
import os
import socket


def initialize_config(params):
    """ Parse env variables or config file to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables first and the in a config file. 
    If at least one of the config parameters is not found a KeyError exception 
    is thrown. If a parameter could not be parsed, a ValueError is thrown. 
    If parsing succeeded, the function returns a ConfigParser object 
    with config parameters
    """

    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        for param, default in params:
            env_param = param.upper()
            default_value = config["DEFAULT"][env_param] if default else None
            config_params[param] = os.getenv(
                env_param, default_value)
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params


def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )


def initialize_workers_environment(config_params):
    config_params["id"] = int(config_params["id"])

    if not config_params["previous_workers"]:
        config_params["previous_workers"] = 0
    else:
        config_params["previous_workers"] = int(
            config_params["previous_workers"])


def get_queue_with_worker_count(queue):
    queue_name, worker_count = queue.split(":")
    return queue_name, int(worker_count)


def get_queue_names(config_params):
    queues_with_count = config_params["output_queues"].split(";")

    return list(
        map(lambda x: get_queue_with_worker_count(x), queues_with_count))


def encode(message):
    return message.encode('utf-8')


def decode(message):
    return message.decode('utf-8')


def add_query_to_message(message, query):
    return f"{query}:{message}"
