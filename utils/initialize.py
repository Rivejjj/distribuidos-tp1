from configparser import ConfigParser
import os
import random
import string

alphabet = string.ascii_lowercase + string.digits


def uuid():
    return ''.join(random.choices(alphabet, k=8))


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


def initialize_log(logging, logging_level):
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
    if "id" not in config_params or not config_params["id"]:
        config_params["id"] = 0
    else:
        config_params["id"] = int(
            config_params["id"])

    if "previous_workers" not in config_params or not config_params["previous_workers"]:
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


def init(logging):
    params = ["logging_level", "id", "input_queue",
              "output_queues", "query", "previous_workers","name"]

    config_params = initialize_config(
        map(lambda param: (param, False), params))

    initialize_workers_environment(config_params)

    initialize_log(logging, config_params["logging_level"])

    if config_params["query"]:
        config_params["query"] = int(config_params["query"])

    return config_params


def encode(message):
    return str(message).encode('utf-8')


def decode(message: bytes):
    return message.decode('utf-8')


def add_query_to_message(message, query):
    return f"{query}:{message}"


def serialize_dict(dic: dict):
    result = {}
    if type(dic) == set:
        return list(dic)
    for key, value in dic.items():
        if type(value) == set:
            result[key] = list(value)
        elif type(value) == dict:
            result[key] = serialize_dict(value)
        else:
            result[key] = value
    return result


def deserialize_dict(dic: dict, top_level=True, convert_to_set=True, convert_to_tuple=False):
    result = {}
    if type(dic) == list and convert_to_set:
        return set(dic)
    elif type(dic) == list and convert_to_tuple:
        return tuple(dic)
    else:
        for key, value in dic.items():

            if key.isdigit() and top_level:
                key = int(key)
            if type(value) == list and convert_to_set:
                result[key] = set(value)
            elif type(value) == list and convert_to_tuple:
                result[key] = tuple(value)
            elif type(value) == dict:
                result[key] = deserialize_dict(
                    value, False, convert_to_set, convert_to_tuple)
            else:
                result[key] = value

    return result
