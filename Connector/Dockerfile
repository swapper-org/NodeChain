FROM python:3

WORKDIR /usr/src/app

COPY . ./
RUN pip3 install -r requirements.txt

EXPOSE 80

RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
