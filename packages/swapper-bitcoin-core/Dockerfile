FROM debian:bullseye-slim

ENV BITCOIN_VERSION=0.21.0
ENV BITCOIN_DATA=/home/bitcoin/.bitcoin
ENV PATH=/opt/bitcoin-${BITCOIN_VERSION}/bin:$PATH
ENV BITCOIN_FILE_HASH_AMD64=da7766775e3f9c98d7a9145429f2be8297c2672fe5b118fd3dc2411fb48e0032
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

EXPOSE 8332 8333 18332 18333 18443 18444 38333 38332

RUN chmod +x entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

RUN bitcoind -version | grep "Bitcoin Core version v${BITCOIN_VERSION}"

CMD ["bitcoind"]