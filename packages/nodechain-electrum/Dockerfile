FROM python:3

WORKDIR /usr/src/app

ENV ELECTRUM_VERSION=4.2.1
ENV ELECTRUM_FILE_HASH=d92c524c7f4fdfcd23d8a6826e45e382640eecadb3f35006e8f300fc43208170

#Download electrum
RUN wget -O Electrum-${ELECTRUM_VERSION}.tar.gz https://download.electrum.org/${ELECTRUM_VERSION}/Electrum-${ELECTRUM_VERSION}.tar.gz \
  && echo "${ELECTRUM_FILE_HASH} Electrum-${ELECTRUM_VERSION}.tar.gz" | sha256sum --check --status \
  && if ! [ $? -eq 0 ]; then exit 1; fi
RUN tar -xzvf Electrum-${ELECTRUM_VERSION}.tar.gz
RUN mv Electrum-${ELECTRUM_VERSION} Electrum

#Install python requirements
RUN pip3 install -r Electrum/contrib/requirements/requirements.txt \
  && pip3 install -r Electrum/contrib/requirements/requirements-binaries.txt

#Install required libraries
RUN apt-get update \
  && apt-get install -y libsecp256k1-dev

#Expose ports
EXPOSE 30000
ENV TESTNET=$TESTNET

#Run app
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
