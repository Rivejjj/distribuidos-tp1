
import logging
import os
from common.reviews_counter import ReviewsCounter
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, initialize_config, initialize_log, initialize_multi_value_environment, initialize_workers_environment
from parser_1.csv_parser import CsvParser
from gateway.common.data_receiver import DataReceiver


def initialize():
    all_params = ["logging_level", "id", "n",
                  "input_queue", "output_queues", "exchange", "query"]

    params = list(map(lambda param: (param, False), all_params))

    config_params = initialize_config(params)
    logging.debug("Config: %s", config_params)
    logging.info("Config: %s", config_params)
    print(config_params)

    if config_params["published_year_range"]:
        config_params["published_year_range"] = tuple(
            map(int, config_params["published_year_range"].split("-")))

    initialize_multi_value_environment(config_params, ["output_queues"])

    initialize_workers_environment(config_params)

    initialize_log(config_params["logging_level"])

    return config_params


def process_message(counter: ReviewsCounter, parser: CsvParser, data_receiver: DataReceiver, queue_middleware: QueueMiddleware, more_than_n, queue=None):
    def callback(ch, method, properties, body):
        msg_received = decode(body)
        if msg_received == "EOF":
            print("EOF received")
            queue_middleware.send_eof()
            return
        book = data_receiver.parse_book(msg_received)
        if book:
            counter.add_book(book)
            print("Book accepted: %s", book.title)
            # queue_middleware.send_to_all(encode(str(book)))
            return

        review = data_receiver.parse_review(msg_received)
        if review:
            author, title, avg = counter.add_review(review)
            if title:
                print("Review forwarded: ", review.title,
                      " | Total reviews: ", avg)
                msg_to_forward = f"{title},{avg}"
                queue_middleware.send_to_all_except(
                    encode(msg_to_forward), "results")
            if title and (title not in more_than_n):
                print("Review accepted: ", review.title,
                      " | Total reviews: ", avg)

                msg_to_result = f"{author},{title}"
                if queue:
                    msg_to_result = add_query_to_message(msg_to_result, queue)
                queue_middleware.send("results", msg_to_result)
                more_than_n[title] = True

    return callback


def main():

    config_params = initialize()
    logging.debug("Config: %s", config_params)

    min_amount_of_reviews = 30
    counter = ReviewsCounter(min_amount_of_reviews)

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), exchange=config_params["exchange"], input_queue=config_params["input_queue"])

    parser = CsvParser()
    data_receiver = DataReceiver()
    more_than_n = {}
    queue_middleware.start_consuming(
        process_message(counter, parser, data_receiver, queue_middleware, more_than_n, queue=config_params["query"]))


if __name__ == "__main__":
    main()
