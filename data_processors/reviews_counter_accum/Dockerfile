FROM rabbitmq-python-base:0.0.1
COPY data_processors/reviews_counter_accum /
COPY entities /entities
COPY rabbitmq /rabbitmq
COPY utils /utils
COPY monitor/monitor_client.py /monitor/monitor_client.py

COPY data_processors/data_manager /data_processors/data_manager
COPY data_checkpoints/data_checkpoint.py /data_checkpoints/data_checkpoint.py
COPY data_checkpoints/messages_checkpoint.py  /data_checkpoints/messages_checkpoint.py
ENTRYPOINT main.py
