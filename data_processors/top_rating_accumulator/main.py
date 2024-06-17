
import logging
from top_rating_manager import TopRatingManager
from utils.initialize import init


def main():

    config_params = init(logging)

    manager = TopRatingManager(config_params)

    manager.run()


if __name__ == "__main__":
    main()
