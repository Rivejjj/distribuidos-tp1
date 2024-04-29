FROM python:3.9.7-slim
RUN pip3 install pika
COPY book-filter /
COPY messages /messages
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY utils /utils

RUN python -m unittest tests/test_filter.py
ENTRYPOINT main.py
