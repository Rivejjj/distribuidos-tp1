import logging
import signal
from functools import partial
from entities.query_message import ANY_IDENTIFIER, REVIEW_IDENTIFIER, QueryMessage
from entities.review import Review
from sentiment_analyzer import SentimentAnalizer
from rabbitmq.queue import QueueMiddleware
from utils.initialize import decode, encode, get_queue_names, initialize_config, initialize_log, initialize_workers_environment
from utils.parser import parse_query_msg, parse_review


def initialize():
    params = ["logging_level", "id", "input_queue",
              "output_queues", "query", "previous_workers"]

    params = list(map(lambda param: (param, False), params))

    config_params = initialize_config(params)

    initialize_log(logging, config_params["logging_level"])
    initialize_workers_environment(config_params)

    return config_params


def process_eof(queue_middleware: QueueMiddleware):
    queue_middleware.send_eof()


def process_review(sentiment_analyzer: SentimentAnalizer, queue_middleware: QueueMiddleware, review: Review):
    polarity_score = sentiment_analyzer.analyze(review.text)

    if not polarity_score:
        return

    message = f"{review.title}\t{polarity_score}"

    query_message = QueryMessage(ANY_IDENTIFIER, message)

    queue_middleware.send_to_all(encode(str(query_message)))


def process_message(sentiment_analyzer: SentimentAnalizer, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        # logging.info("Received message", decode(body))
        msg_received = decode(body)
        if msg_received == "EOF":
            print("Received EOF")
            process_eof(queue_middleware)
            return

        identifier, data = parse_query_msg(msg_received)

        if identifier == REVIEW_IDENTIFIER:
            process_review(sentiment_analyzer,
                           queue_middleware, parse_review(data))
    return callback


def handle_sigterm(queue_middleware: QueueMiddleware):
    #queue_middleware.handle_sigterm()
    logging.info("Stopping consuming...")
    queue_middleware.stop_consuming()
    #queue_middleware.connection.close()


def main():

    config_params = initialize()

    sentiment_analyzer = SentimentAnalizer()

    queue_middleware = QueueMiddleware(
        get_queue_names(config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    # signal.signal(signal.SIGTERM, lambda signal,frame: handle_sigterm(queue_middleware))

    queue_middleware.start_consuming(
        process_message(sentiment_analyzer, queue_middleware))


if __name__ == "__main__":
    main()
