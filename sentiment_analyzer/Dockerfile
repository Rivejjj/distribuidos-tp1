FROM python:3.9.7-slim
COPY reviews_counter_accum /
COPY messages /messages
RUN python -m unittest tests/test_accum.py
ENTRYPOINT ["/bin/sh"]