
from configparser import ConfigParser
import logging
import os
from common.book_filter import BookFilter
from messages.book import Book
import pika
import time
import functools

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
            'LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["category"] = os.getenv(
            'CATEGORY', None)
        config_params["published_year_range"] = os.getenv(
            'PUBLISHED_YEAR_RANGE', None)
        config_params["title_contains"] = os.getenv(
            'TITLE_CONTAINS', None)

        if config_params["published_year_range"]:
            config_params["published_year_range"] = tuple(
                map(int, config_params["published_year_range"].split("-")))
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

def callback2(ch, method, properties, body, args):
    logging.info(f" [x] {method.routing_key}:{body}")
    fields = body.decode().split(",")
    book = Book(*fields)
    if not book.has_empty_fields() and args[0].filter(body):
        args[1].write(body)
        logging.info(f"{body}\n")

def callback(ch, method, properties, body):
    logging.info(f" [x] {method.routing_key}:{body}")


def declare_exchange():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')
    return channel


def main():
    config_params = initialize_config()
    initialize_log(config_params["logging_level"])
    logging.debug("Config: %s", config_params)

    book_filter = BookFilter(
        category=config_params["category"],
        published_year_range=config_params["published_year_range"],
        title_contains=config_params["title_contains"]
    )
    time.sleep(40)

    channel = declare_exchange()

    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    binding_key = "book"

    channel.queue_bind(
        exchange='topic_logs', queue=queue_name, routing_key=binding_key)
    
    logging.info(' [*] Waiting for logs. To exit press CTRL+C')
    

    filtered = open("filtered_books.csv", "w")
    
    #args = (book_filter, filtered)
    #callback = functools.partial(callback2, args=args)

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()



if __name__ == "__main__":
    main()
