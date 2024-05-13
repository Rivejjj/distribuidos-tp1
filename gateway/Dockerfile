FROM rabbitmq-python-base:0.0.1
COPY gateway /
COPY entities /entities
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY utils /utils
ENTRYPOINT ["/bin/sh"]