
from configparser import ConfigParser
import logging
import os
from parser_1.csv_parser import CsvParser
from rabbitmq.queue import QueueMiddleware
from data_processors.sentiment_score_accumulator.sentiment_score_accumulator import SentimentScoreAccumulator
from messages.book import Book
from utils.initialize import add_query_to_message, encode, get_queue_names, initialize_config, initialize_log, decode, initialize_workers_environment


def initialize():
    params = ["logging_level", "id", "input_queue",
              "output_queues", "query", "previous_workers"]

    config_params = initialize_config(
        map(lambda param: (param, False), params))

    initialize_workers_environment(config_params)

    initialize_log(config_params["logging_level"])

    return config_params


def parse_message(msg_received):
    line = CsvParser().parse_csv(msg_received)

    if len(line) != 2:
        return None
    title, score = line
    return title, float(score)


def send_results(sentiment_acc: SentimentScoreAccumulator, queue_middleware: QueueMiddleware, query=None):
    for title, score in sentiment_acc.calculate_90th_percentile():
        print(f"[SENTIMENT RESULT]: {title}, {score}")
        message = f"{title},{score}"

        if query:
            message = add_query_to_message(message, query)
        queue_middleware.send_to_all(encode(message))


def process_eof(queue_middleware: QueueMiddleware, sentiment_acc: SentimentScoreAccumulator, query=None):
    def callback():
        send_results(sentiment_acc, queue_middleware, query)
        sentiment_acc.clear()
    queue_middleware.send_eof(callback)


def process_message(sentiment_acc: SentimentScoreAccumulator, queue_middleware: QueueMiddleware, query=None):
    def callback(ch, method, properties, body):
        # print("Received message", decode(body))
        msg_received = decode(body)

        if msg_received == "EOF":
            print("Received EOF")
            process_eof(queue_middleware, sentiment_acc, query)
            return

        line = parse_message(msg_received)

        if not line:
            return

        sentiment_acc.add_sentiment_score(*line)

    return callback


def main():

    config_params = initialize()

    accumulator = SentimentScoreAccumulator(10)

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    queue_middleware.start_consuming(
        process_message(accumulator, queue_middleware, config_params["query"]))


if __name__ == "__main__":
    main()
