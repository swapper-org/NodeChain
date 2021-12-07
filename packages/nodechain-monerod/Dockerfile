# Usage: docker run --restart=always -v /var/data/blockchain-xmr:/root/.bitmonero -p 18080:18080 -p 18081:18081 --name=monerod -td kannix/monero-full-node
FROM debian:bullseye-slim AS build

ENV MONERO_VERSION=0.17.2.3 MONERO_SHA256=8069012ad5e7b35f79e35e6ca71c2424efc54b61f6f93238b182981ba83f2311

RUN apt-get update && apt-get install -y curl bzip2 gosu

WORKDIR /root

RUN curl https://dlsrc.getmonero.org/cli/monero-linux-x64-v$MONERO_VERSION.tar.bz2 -O &&\
  echo "$MONERO_SHA256  monero-linux-x64-v$MONERO_VERSION.tar.bz2" | sha256sum -c - &&\
  tar -xvf monero-linux-x64-v$MONERO_VERSION.tar.bz2 &&\
  rm monero-linux-x64-v$MONERO_VERSION.tar.bz2 &&\
  cp ./monero-x86_64-linux-gnu-v$MONERO_VERSION/monerod . &&\
  rm -r monero-*

FROM debian:bullseye-slim

RUN useradd -ms /bin/bash monero && mkdir -p /home/monero/.bitmonero && chown -R monero:monero /home/monero/.bitmonero
USER monero
WORKDIR /home/monero

COPY --chown=monero:monero --from=build /root/monerod /home/monero/monerod

VOLUME /home/monero/.bitmonero

EXPOSE 18080 18081 38080 38081 


COPY --chown=monero:monero entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh
ENTRYPOINT ["/home/monero/entrypoint.sh"]

ENTRYPOINT ["./monerod"]