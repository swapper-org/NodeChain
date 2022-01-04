FROM python:3

WORKDIR /usr/src/app

ENV ELECTRON_VERSION=4.2.6
ENV ELECTRON_FILE_HASH=3fbcb81c8efc005450595cbff975e44ebb77473e2b14ca27f6863efbf96b2f91

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
