
from configparser import ConfigParser
import logging
import os
from messages.book import Book
import pika
import time

BOOKS_DATA_PATH = "books_data.csv"


def initialize_config():
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
        config_params["logging_level"] = os.getenv(
            "LOGGING_LEVEL", config["DEFAULT"]["LOGGING_LEVEL"])
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

def read_csv(file):
	line = file.readline()
	line = line.strip('\n')
	return line
	

def main():
    config_params = initialize_config()
    initialize_log(config_params["logging_level"])

    logging.debug("Config: %s", config_params)
    logging.info("Starting book filter")

    time.sleep(40)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

    file = open(BOOKS_DATA_PATH, 'r', encoding="utf8")
    message = read_csv(file)

    routing_key = "book"

    for _ in range(1,20):
        channel.basic_publish(
            exchange='topic_logs', routing_key=routing_key, body=message)
        logging.info(f" [x] Sent {routing_key}:{message}")
        message = read_csv(file)

    time.sleep(25)


if __name__ == "__main__":
    main()