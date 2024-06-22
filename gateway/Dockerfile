FROM rabbitmq-python-base:0.0.1
COPY gateway /
COPY entities /entities
COPY rabbitmq /rabbitmq
COPY data_checkpoints/data_checkpoint.py /data_checkpoints/data_checkpoint.py
COPY data_checkpoints/messages_checkpoint.py  /data_checkpoints/messages_checkpoint.py
COPY utils /utils
ENTRYPOINT ["/bin/sh"]