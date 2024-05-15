import signal
import logging
from top_rating_accumulator import TopRatingAccumulator
from entities.query_message import ANY_IDENTIFIER, QueryMessage
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, initialize_config, initialize_log, initialize_workers_environment
from utils.parser import DATA_SEPARATOR, parse_query_msg, split_line


def initialize():
    all_params = ["logging_level", "id",
                  "input_queue", "output_queues", "query", "previous_workers"]

    params = list(map(lambda param: (param, False), all_params))

    config_params = initialize_config(params)

    initialize_workers_environment(config_params)

    initialize_log(logging, config_params["logging_level"])

    return config_params


def process_eof(queue_middleware: QueueMiddleware, accum: TopRatingAccumulator, query=None):
    def callback():
        logging.info("EOF received")
        top = accum.get_top()
        result = ""
        for i in top:
            result += f"{i[0]},{i[1]}\n"
        logging.info(f"sending to result: {result}")

        msg = add_query_to_message(result, query)
        query_msg = QueryMessage(ANY_IDENTIFIER, msg)
        queue_middleware.send_to_all(
            encode(str(query_msg)))
        accum.clear()

    queue_middleware.send_eof(callback)


def process_message(accum: TopRatingAccumulator, queue_middleware: QueueMiddleware, query):
    def callback(ch, method, properties, body):
        msg_received = decode(body)
        if msg_received == "EOF":
            process_eof(queue_middleware, accum, query)
            return

        _, data = parse_query_msg(msg_received)

        data = split_line(data, DATA_SEPARATOR)

        if len(data) == 2:
            logging.info(f"Received: {data}")
            title, avg_rating = data
            # print("Book accepted: ", book)
            accum.add_title(title, avg_rating)

    return callback


def main():

    config_params = initialize()
    logging.debug("Config: %s", config_params)

    top = 10
    accum = TopRatingAccumulator(top)

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])
    signal.signal(signal.SIGTERM, lambda signal, frame:  queue_middleware.handle_sigterm())
    queue_middleware.start_consuming(
        process_message(accum, queue_middleware, config_params["query"]))


if __name__ == "__main__":
    main()
