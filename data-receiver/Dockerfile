FROM rabbitmq-python-base:0.0.1
COPY data-receiver /
COPY messages /messages
COPY rabbitmq/queue.py /rabbitmq/queue.py
RUN python -m unittest tests/test_data_receiver.py
ENTRYPOINT main.py
