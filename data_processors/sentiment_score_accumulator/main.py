import logging
from sentiment_accumulator_manager import SentimentAccumulatorManager
from utils.initialize import init


def main():

    config_params = init(logging)

    manager = SentimentAccumulatorManager(config_params)

    manager.run()


if __name__ == "__main__":
    main()
