FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt ./Connector/requirements.txt
RUN pip3 install -r Connector/requirements.txt

ENV API_KEY=$API_KEY

COPY . ./Connector

EXPOSE 80 28332

RUN chmod +x Connector/docker-entrypoint.sh
ENTRYPOINT ["/usr/src/app/Connector/docker-entrypoint.sh"]
