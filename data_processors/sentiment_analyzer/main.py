import logging
from entities.query_message import REVIEW, TITLE_SCORE, QueryMessage
from entities.review import Review
from sentiment_analyzer import SentimentAnalizer
from rabbitmq.queue import QueueMiddleware
from utils.initialize import decode, encode, get_queue_names, init
from utils.parser import parse_query_msg, parse_review


def process_eof(queue_middleware: QueueMiddleware):
    queue_middleware.send_eof()


def process_review(sentiment_analyzer: SentimentAnalizer, queue_middleware: QueueMiddleware, review: Review):
    polarity_score = sentiment_analyzer.analyze(review.text)

    if not polarity_score:
        return

    message = f"{review.title}\t{polarity_score}"

    query_message = QueryMessage(TITLE_SCORE, message)

    queue_middleware.send_to_all(encode(str(query_message)))


def process_message(sentiment_analyzer: SentimentAnalizer, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        # logging.info("Received message", decode(body))
        msg_received = decode(body)
        if msg_received == "EOF":
            logging.info("Received EOF")
            process_eof(queue_middleware)
            return

        identifier, data = parse_query_msg(msg_received)

        if identifier == REVIEW:
            logging.info("Received review")
            process_review(sentiment_analyzer,
                           queue_middleware, parse_review(data))
    return callback


def main():

    config_params = init(logging)

    sentiment_analyzer = SentimentAnalizer()

    queue_middleware = QueueMiddleware(
        get_queue_names(config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    queue_middleware.start_consuming(
        process_message(sentiment_analyzer, queue_middleware))


if __name__ == "__main__":
    main()
