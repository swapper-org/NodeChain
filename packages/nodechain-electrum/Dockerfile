FROM python:3

WORKDIR /usr/src/app

ENV ELECTRUM_VERSION=4.1.5
ENV ELECTRUM_FILE_HASH=91472e281f604a7a687faa4b339bf5e484bd2bec82a495ea45bfa014e52719a1

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
