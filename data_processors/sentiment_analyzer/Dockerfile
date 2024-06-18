FROM rabbitmq-python-base:0.0.1
COPY data_processors/sentiment_analyzer /
COPY entities /entities
COPY rabbitmq/queue.py /rabbitmq/queue.py
COPY utils /utils
COPY data_processors/data_manager /data_processors/data_manager
COPY data_checkpoints/data_checkpoint.py /data_checkpoints/data_checkpoint.py
COPY data_checkpoints/messages_checkpoint.py  /data_checkpoints/messages_checkpoint.py
RUN pip3 install textblob
ENTRYPOINT ["/bin/sh"]