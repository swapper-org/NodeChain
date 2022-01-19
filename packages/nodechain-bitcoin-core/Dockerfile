FROM debian:bullseye-slim

ENV BITCOIN_VERSION=0.21.1
ENV BITCOIN_DATA=/home/bitcoin/.bitcoin
ENV PATH=/opt/bitcoin-${BITCOIN_VERSION}/bin:$PATH
ENV BITCOIN_FILE_HASH_AMD64=366eb44a7a0aa5bd342deea215ec19a184a11f2ca22220304ebb20b9c8917e2b
ENV PLATFORM=x86_64-linux-gnu

RUN useradd -r bitcoin \
  && apt-get update -y \
  && apt-get install -y curl gosu \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN curl -SLO https://bitcoin.org/bin/bitcoin-core-${BITCOIN_VERSION}/bitcoin-${BITCOIN_VERSION}-${PLATFORM}.tar.gz \
  && echo "${BITCOIN_FILE_HASH_AMD64} bitcoin-${BITCOIN_VERSION}-${PLATFORM}.tar.gz" | sha256sum --check --status \
  && if ! [ $? -eq 0 ]; then exit 1; fi \
  && tar -xzf *.tar.gz -C /opt \
  && rm *.tar.gz \
  && rm -rf /opt/bitcoin-${BITCOIN_VERSION}/bin/bitcoin-qt

COPY entrypoint.sh /entrypoint.sh

VOLUME ["/home/bitcoin/.bitcoin"]

EXPOSE 8332 8333 18332 18333 18443 18444 38333 38332 28332

RUN chmod +x entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

RUN bitcoind -version | grep "Bitcoin Core version v${BITCOIN_VERSION}"

CMD ["bitcoind"]