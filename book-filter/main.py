
from configparser import ConfigParser
import logging
import os
from common.book_filter import BookFilter
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


def main():

    config_params = initialize_config()
    initialize_log(config_params["logging_level"])

    logging.debug("Config: %s", config_params)

    book_filter = BookFilter(
        category=config_params["category"],
        published_year_range=config_params["published_year_range"],
        title_contains=config_params["title_contains"]
    )

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

    book_filter.filter(test_book)
