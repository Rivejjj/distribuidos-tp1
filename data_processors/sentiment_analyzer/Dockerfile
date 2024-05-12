FROM rabbitmq-python-base:0.0.1
COPY data_processors/sentiment_analyzer /
COPY entities /entities
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY utils /utils

RUN pip3 install textblob
ENTRYPOINT ["/bin/sh"]