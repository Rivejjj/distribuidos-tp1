
import logging
from reviews_counter_manager import ReviewsCounterManager
from utils.initialize import init


def main():

    config_params = init(logging)

    manager = ReviewsCounterManager(config_params)

    manager.run()


if __name__ == "__main__":
    main()
