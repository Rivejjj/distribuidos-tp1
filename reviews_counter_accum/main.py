
import logging
import os
from common.reviews_counter import ReviewsCounter
from rabbitmq.queue import QueueMiddleware
from utils.initialize import encode, initialize_config, initialize_log
from parser_1.csv_parser import CsvParser
from gateway.common.data_receiver import DataReceiver

def initialize():
    all_params = ["logging_level", "category",
                  "published_year_range", "title_contains", "id", "last", "input_queue", "output_queue", "exchange", "save_books"]
    env = os.environ
    params = []
    for param in all_params:
        param = param.upper()
        if param in env:
            params.append((param, True))
        else:
            params.append((param, False))

    config_params = initialize_config(params)
    logging.debug("Config: %s", config_params)
    logging.info("Config: %s", config_params)
    print(config_params)

    if config_params["PUBLISHED_YEAR_RANGE"]:
        config_params["PUBLISHED_YEAR_RANGE"] = tuple(
            map(int, config_params["PUBLISHED_YEAR_RANGE"].split("-")))

    if "LAST" in config_params:
        config_params["LAST"] = bool(config_params["LAST"])

    if "ID" in config_params:
        config_params["ID"] = int(config_params["ID"])

    initialize_log(config_params["LOGGING_LEVEL"])

    return config_params



def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )

def get_queue_names(config_params):
    return [config_params["OUTPUT_QUEUE"]]


def process_message(counter: ReviewsCounter,parser: CsvParser, data_receiver: DataReceiver, queue_middleware: QueueMiddleware):
    def callback(ch, method, properties, body):
        msg_received = body.decode()
        book = data_receiver.parse_book(msg_received)

        if book:
            counter.add_book(book)
            print("Book accepted: %s", book.title)
            queue_middleware.send_to_all(encode(str(book)))
            return

        review = data_receiver.parse_review(msg_received)
        if review:
            title, amount = counter.add_review(review)
            if title:
                print("Review accepted: ", review.title," | Total reviews: ", amount)
                queue_middleware.send_to_all(encode(str(review)))


    return callback




def main():

    config_params = initialize()
    initialize_log(config_params["LOGGING_LEVEL"])
    logging.debug("Config: %s", config_params)

    counter = ReviewsCounter()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), exchange=config_params["EXCHANGE"], input_queue=config_params["INPUT_QUEUE"])

    parser = CsvParser()
    data_receiver = DataReceiver()
    queue_middleware.start_consuming(
        process_message(counter, parser,data_receiver, queue_middleware))




if __name__ == "__main__":
    main()