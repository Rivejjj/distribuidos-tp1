FROM python:3.9.7-slim
COPY decades_accumulator /
COPY messages /messages
RUN python -m unittest tests/test_accum.py
ENTRYPOINT ["/bin/sh"]