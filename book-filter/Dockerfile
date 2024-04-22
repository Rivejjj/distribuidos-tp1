FROM python:3.9.7-slim
COPY book-filter /
COPY messages /messages
RUN python -m unittest tests/test_filter.py
ENTRYPOINT ["/bin/sh"]
