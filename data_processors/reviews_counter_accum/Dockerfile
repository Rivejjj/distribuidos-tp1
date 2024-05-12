FROM rabbitmq-python-base:0.0.1
COPY data_processors/reviews_counter_accum /
COPY entities /entities
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY utils /utils
ENTRYPOINT main.py
