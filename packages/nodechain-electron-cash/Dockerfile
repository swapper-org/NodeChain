FROM python:3

WORKDIR /usr/src/app

ENV ELECTRON_VERSION=4.2.4
ENV ELECTRON_FILE_HASH=2754d3177f05d08e77622a9cc8966153d290d8a8a816db9da309aaafcb09792c

#Download electron cash
RUN wget -O Electron-Cash-${ELECTRON_VERSION} https://github.com/Electron-Cash/Electron-Cash/releases/download/${ELECTRON_VERSION}/Electron-Cash-${ELECTRON_VERSION}.tar.gz \
  && echo "${ELECTRON_FILE_HASH} Electron-Cash-${ELECTRON_VERSION}" | sha256sum --check --status \
  && if ! [ $? -eq 0 ]; then exit 1; fi
RUN tar -xzvf Electron-Cash-${ELECTRON_VERSION}
RUN mv Electron-Cash-${ELECTRON_VERSION} Electron-Cash

#Install python requirements
RUN pip3 install -r Electron-Cash/contrib/requirements/requirements.txt

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
