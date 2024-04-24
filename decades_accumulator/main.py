
from configparser import ConfigParser
import logging
import os
from common.accumulator import Accumulator
from messages.book import Book


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
        config_params["logging_level"] = os.getenv("LOGGING", config["DEFAULT"]["LOGGING_LEVEL"])
        
    except KeyError as e:
        raise KeyError(f"Missing configuration parameter: {e}. Aborting server")
    except ValueError as e:
        raise ValueError(f"Error parsing configuration parameter: {e}. Aborting server")

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


def main():

    config_params = initialize_config()
    initialize_log(config_params["logging_level"])

    logging.debug("Config: %s", config_params)

    accum = Accumulator()

    test_book = Book(
        "Test Book",
        "Test Description",
        "Test Author",
        "Test Image",
        "Test Preview Link",
        "Test Publisher",
        "2021-01-01",
        "Test Info Link",
        ["literature", "fiction"],
        1
    )

    accum.add_book(test_book)
