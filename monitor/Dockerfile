FROM python:3.7-alpine
RUN apk update && apk add docker
# RUN pip install docker-compose

COPY utils /utils
COPY monitor /
COPY docker-compose-dev.yaml /
COPY revive.sh /
COPY data_processors /data_processors

RUN chmod +x /revive.sh


# WORKDIR /src
ENTRYPOINT ["/bin/sh"]