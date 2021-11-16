FROM debian:bullseye-slim

ENV MONERO_VERSION=0.17.2.3
ENV BITCOIN_DATA=/home/bitcoin/.bitcoin
ENV PATH=/opt/bitcoin-${BITCOIN_VERSION}/bin:$PATH
ENV BITCOIN_FILE_HASH_AMD64=8069012ad5e7b35f79e35e6ca71c2424efc54b61f6f93238b182981ba83f2311
ENV PLATFORM=x86_64-linux-gnu

RUN useradd -r bitcoin \
  && apt-get update -y \
  && apt-get install -y curl gosu \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN curl -SLO https://downloads.getmonero.org/cli/monero-gui-linux-x64-v${BITCOIN_VERSION}.tar.bz2 \
  && echo "${BITCOIN_FILE_HASH_AMD64} bitcoin-${BITCOIN_VERSION}-${PLATFORM}.tar.gz" | sha256sum --check --status \
  && if ! [ $? -eq 0 ]; then exit 1; fi \
  && tar -xzf *.tar.gz -C /opt \
  && rm *.tar.gz \
  && rm -rf /opt/bitcoin-${BITCOIN_VERSION}/bin/bitcoin-qt

COPY entrypoint.sh /entrypoint.sh

VOLUME ["/home/bitcoin/.bitcoin"]

EXPOSE 8332 8333 18332 18333 18443 18444 38333 38332

RUN chmod +x entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

RUN bitcoind -version | grep "Bitcoin Core version v${BITCOIN_VERSION}"

CMD ["bitcoind"]