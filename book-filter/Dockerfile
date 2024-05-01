FROM rabbitmq-python-base:0.0.1
COPY book-filter /
COPY messages /messages
COPY parser_1 /parser_1
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY rabbitmq/eof_queue.py /rabbitmq/eof_queue.py
COPY utils /utils

RUN python -m unittest tests/test_filter.py
ENTRYPOINT main.py
