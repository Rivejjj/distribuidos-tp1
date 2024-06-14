import logging
from multiprocessing import Process
from top_rating_accumulator import TopRatingAccumulator
from entities.query_message import TITLE_SCORE, QueryMessage
from rabbitmq.queue import QueueMiddleware
from utils.initialize import add_query_to_message, decode, encode, get_queue_names, init
from utils.parser import DATA_SEPARATOR, parse_query_msg, split_line
from monitor.monitor_client import MonitorClient


def send_heartbeat(address, port, name):
    monitor_client = MonitorClient(address, port, name)
    monitor_client.run()

def process_eof(queue_middleware: QueueMiddleware, accum: TopRatingAccumulator, query=None):
    def callback():
        logging.info("EOF received")
        top = accum.get_top()
        result = ""
        for i in top:
            result += f"{i[0]}\t{i[1]}\n"
        logging.info(f"sending to result: {result}")

        msg = add_query_to_message(result, query)
        query_msg = QueryMessage(TITLE_SCORE, msg)
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

        identifier, data = parse_query_msg(msg_received)

        if identifier != TITLE_SCORE:
            return

        data = split_line(data, DATA_SEPARATOR)

        if len(data) == 2:
            logging.info(f"Received: {data}")
            title, avg_rating = data
            accum.add_title(title, avg_rating)

    return callback


def main():

    config_params = init(logging)

    top = 10
    accum = TopRatingAccumulator(top)

    process = Process(target=send_heartbeat, args=(
        "monitor", 22223, config_params["name"]))
    process.start()

    queue_middleware = QueueMiddleware(get_queue_names(
        config_params), input_queue=config_params["input_queue"], id=config_params["id"], previous_workers=config_params["previous_workers"])

    try:
        queue_middleware.start_consuming(
            process_message(accum, queue_middleware, config_params["query"]))
    except OSError as e :
        logging.error(f"Error while consuming from queue {e}")
    except AttributeError as e :
        logging.error(f"Error while consuming from queue: {e}")

if __name__ == "__main__":
    main()
