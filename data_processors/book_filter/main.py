from multiprocessing import Process
import logging
from rabbitmq.queue import QueueMiddleware
from utils.initialize import get_queue_names, init, initialize_config
from book_filter import BookFilter
from review_filter import ReviewFilter
from monitor.monitor_client import MonitorClient
import logging
from filter_manager import FilterManager
from utils.initialize import init, initialize_config


def send_heartbeat(name):
    logging.warning(f"Starting monitor client with name {name}")
    monitor_client = MonitorClient(name)
    monitor_client.run()


def initialize():
    all_params = ["category",
                  "published_year_range", "title_contains", "save_books", "is_equal", "no_send", "name"]

    params = list(map(lambda param: (param, False), all_params))

    filter_config_params = initialize_config(params)

    if filter_config_params["published_year_range"]:
        filter_config_params["published_year_range"] = tuple(
            map(int, filter_config_params["published_year_range"].split("-")))

    if filter_config_params["save_books"]:
        filter_config_params["save_books"] = True

    config_params = init(logging)

    config_params.update(filter_config_params)
    return config_params


def main():
    config_params = initialize()


<< << << < HEAD
 book_filter = BookFilter(
      category=config_params["category"],
      published_year_range=config_params["published_year_range"],
      title_contains=config_params["title_contains"],
      is_equal=config_params["is_equal"]
      )

  review_filter = None

   if config_params["save_books"]:
        review_filter = ReviewFilter()

    name = config_params["name"]
    process = Process(target=send_heartbeat, args=(name,))
    process.daemon = True
    process.start()

    logging.warning("Starting book filter")

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    try:
        queue_middleware.start_consuming(
            process_message(book_filter, review_filter, queue_middleware, config_params["query"]))

    except OSError as e:
        logging.error(f"Error while consuming from queue {e}")
    except AttributeError as e:
        logging.error(f"Error while consuming from queue: {e}")
== == == =

 manager = FilterManager(config_params)

  manager.run()
>>>>>> > origin/main


if __name__ == "__main__":
    main()
