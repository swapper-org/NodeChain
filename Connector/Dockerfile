FROM python:3.7

WORKDIR /usr/src/app

COPY . ./Connector
RUN pip3 install -r Connector/requirements.txt

EXPOSE 80 28332

RUN chmod +x Connector/docker-entrypoint.sh
ENTRYPOINT ["/usr/src/app/Connector/docker-entrypoint.sh"]
