FROM rabbitmq-python-base:0.0.1
COPY data_processors/book_filter /
COPY entities /entities
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY utils /utils
COPY monitor/monitor_client.py /monitor/monitor_client.py

ENTRYPOINT main.py
