FROM rabbitmq-python-base:0.0.1
COPY gateway /
COPY parser_1/ /parser_1
COPY messages /messages
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY utils /utils
COPY rabbitmq/eof_queue.py /rabbitmq/eof_queue.py

RUN python -m unittest tests/test_data_receiver.py
ENTRYPOINT ["/bin/sh"]