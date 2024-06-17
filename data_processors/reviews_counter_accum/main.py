
import logging
from reviews_counter_manager import ReviewsCounterManager
from utils.initialize import init


def main():

    config_params = init(logging)

    manager = ReviewsCounterManager(config_params)

<<<<<<< HEAD
    min_amount_of_reviews = 500
    counter = ReviewsCounter(min_amount_of_reviews)

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    more_than_n = {}
    try:
        queue_middleware.start_consuming(
            process_message(counter, queue_middleware, more_than_n, query=config_params["query"]))
    except OSError as e:
        logging.error(f"Error while consuming from queue {e}")
    except AttributeError as e :
        logging.error(f"Error while consuming from queue: {e}")
=======
    manager.run()

>>>>>>> c3a6dc1 (Reviews Counter finished)

if __name__ == "__main__":
    main()
