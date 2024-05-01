FROM rabbitmq-python-base:0.0.1
COPY accumulator /
COPY messages /messages
COPY gateway /gateway
COPY parser_1 /parser_1
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY utils /utils
RUN python -m unittest tests/test_accum.py
ENTRYPOINT main.py
