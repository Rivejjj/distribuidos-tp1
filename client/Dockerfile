FROM python:3.9.7-slim
COPY client /
COPY messages /messages
RUN pip install pika
ENTRYPOINT ["/bin/sh"]
