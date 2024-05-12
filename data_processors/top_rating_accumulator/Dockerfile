FROM rabbitmq-python-base:0.0.1
COPY data_processors/top_rating_accumulator /
COPY entities /entities
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY utils /utils
ENTRYPOINT main.py
