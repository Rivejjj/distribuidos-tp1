FROM rabbitmq-python-base:0.0.1
COPY decades-accumulator /
COPY messages /messages
COPY parser_1 /parser_1
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY utils /utils

RUN python -m unittest tests/test_accum.py
ENTRYPOINT main.py
