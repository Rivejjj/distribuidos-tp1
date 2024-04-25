FROM python:3.9.7-slim
COPY data-receiver /
COPY messages /messages
RUN python -m unittest tests/test_data_receiver.py
ENTRYPOINT ["/bin/sh"]