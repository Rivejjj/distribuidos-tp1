FROM rabbitmq-python-base:0.0.1
COPY gateway /
COPY messages /messages
COPY rabbitmq/queue.py /rabbitmq/queue.py

COPY utils /utils
RUN pip3 install pika
RUN python -m unittest tests/test_data_receiver.py
ENTRYPOINT ["/bin/sh"]