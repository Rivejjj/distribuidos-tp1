
from configparser import ConfigParser
import logging
import os
from common.sentiment_analyzer import SentimentAnalizer
from messages.book import Book
from messages.review import Review
from parser_1.csv_parser import CsvParser
from rabbitmq.queue import QueueMiddleware
from utils.initialize import decode, encode, get_queue_names, initialize_config, initialize_log


def initialize():
    all_params = ["logging_level", "input_queue",
                  "output_queues", "exchange"]

    params = list(map(lambda param: (param, False), all_params))

    config_params = initialize_config(params)
    logging.debug("Config: %s", config_params)
    logging.info("Config: %s", config_params)
    print(config_params)

    initialize_log(config_params["logging_level"])

    return config_params


def process_eof(queue_middleware: QueueMiddleware):
    queue_middleware.send_eof()


def process_message(sentiment_analyzer: SentimentAnalizer, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        logging.info("Received message", decode(body))
        msg_received = decode(body)

        if msg_received == "EOF":
            process_eof(queue_middleware)
            return

        line = CsvParser().parse_csv(msg_received)

        review = Review(*line)

        if review and review.sanitize():
            print(f"[REVIEW]: Text {review.text}")
            polarity_score = sentiment_analyzer.analyze(review.text)

            if not polarity_score:
                return

            print(f"[POLARITY SCORE]: {polarity_score}")

            message = f"{review.title},{polarity_score}"

            print(f"[RESULT]: {message}")

            queue_middleware.send_to_all(encode(message))

    return callback


def main():

    config_params = initialize()

    sentiment_analyzer = SentimentAnalizer()

    queue_middleware = QueueMiddleware(
        get_queue_names(config_params), input_queue=config_params["input_queue"], exchange=config_params["exchange"])

    queue_middleware.start_consuming(
        process_message(sentiment_analyzer, queue_middleware))


if __name__ == "__main__":
    main()
