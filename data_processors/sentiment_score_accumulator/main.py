import logging
from entities.query_message import TITLE_SCORE, QueryMessage
from rabbitmq.queue import QueueMiddleware
from sentiment_score_accumulator import SentimentScoreAccumulator
from utils.initialize import add_query_to_message, encode, get_queue_names, decode, init
from utils.parser import parse_query_msg, split_line


def send_results(sentiment_acc: SentimentScoreAccumulator, queue_middleware: QueueMiddleware, query=None):
    for title, score in sentiment_acc.calculate_90th_percentile():
        print(f"[SENTIMENT RESULT]: {title}, {score}")
        message = f"{title}\t{score}"

        if query:
            message = add_query_to_message(message, query)

        query_message = QueryMessage(TITLE_SCORE, message)
        queue_middleware.send_to_all(encode(str(query_message)))


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
            process_eof(queue_middleware, sentiment_acc, query)
            return

        identifier, message = parse_query_msg(msg_received)

        if identifier == TITLE_SCORE:
            title, score = split_line(message, '\t')
            logging.info(f"Received: {title}, {score}")

            sentiment_acc.add_sentiment_score(title, score)

    return callback


def main():

    config_params = init(logging)

    accumulator = SentimentScoreAccumulator()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    try:
        queue_middleware.start_consuming(
            process_message(accumulator, queue_middleware, config_params["query"]))
    except OSError as e:
        logging.error(f"Error while consuming from queue {e}")
    except AttributeError as e :
        logging.error(f"Error while consuming from queue: {e}")

if __name__ == "__main__":
    main()
