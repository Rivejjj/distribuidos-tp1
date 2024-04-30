
from configparser import ConfigParser
import logging
import os
from parser_1.csv_parser import CsvParser
from rabbitmq.queue import QueueMiddleware
from sentiment_score_accumulator.common.sentiment_score_accumulator import SentimentAnalizer, SentimentScoreAccumulator
from messages.book import Book
from utils.initialize import encode, get_queue_names, initialize_config, initialize_log, initialize_multi_value_environment, initialize_workers_environment, decode


def initialize():
    params = ["logging_level", "id", "n", "input_queue",
              "output_queues"]

    config_params = initialize_config(
        map(lambda param: (param, False), params))

    initialize_multi_value_environment(config_params, ["output_queues"])

    initialize_workers_environment(config_params)

    initialize_log(config_params["logging_level"])

    return config_params


def parse_message(msg_received):
    line = CsvParser().parse_csv(msg_received)

    if len(line) != 2:
        return None
    title, score = line
    return title, int(score)


def send_results(sentiment_acc: SentimentScoreAccumulator, queue_middleware: QueueMiddleware):
    for title, score in sentiment_acc.get_sentiment_scores():
        queue_middleware.send_to_all(encode(f"{title},{score}"))


def process_message(sentiment_acc: SentimentScoreAccumulator, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        logging.info("Received message", body.decode())
        msg_received = decode(body)

        if msg_received == "EOF":
            send_results(sentiment_acc, queue_middleware)
            sentiment_acc.clear()
            return

        line = parse_message(msg_received)
        if not line:
            return

        sentiment_acc.add_sentiment_score(*line)

    return callback


def main():

    config_params = initialize()

    accumulator = SentimentScoreAccumulator()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), exchange=config_params["exchange"], input_queue=config_params["input_queue"])

    queue_middleware.start_consuming(
        process_message(accumulator, queue_middleware))
