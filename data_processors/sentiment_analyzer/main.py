import logging
from sentiment_analyzer_manager import SentimentAnalyzerManager
from utils.initialize import init


def main():

    config_params = init(logging)

    manager = SentimentAnalyzerManager(config_params)

    manager.run()


if __name__ == "__main__":
    main()
