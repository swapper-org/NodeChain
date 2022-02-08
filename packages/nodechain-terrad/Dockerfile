FROM debian:bullseye-slim

ARG VERSION=v0.5.16

WORKDIR /root

RUN apt-get update && apt-get install -y build-essential git wget
# RUN apk add build-base && apk add git

COPY --from=golang:1.17.6-bullseye /usr/local/go/ /usr/local/go/

ENV PATH="$PATH:/usr/local/go/bin"

RUN git clone https://github.com/terra-money/core && cd core && git checkout ${VERSION}
RUN cd core && make install

ENV PATH="$PATH:/root/go/bin"

# Default P2P protocol 26656, API REST 1317, RPC 26657 (only public nodes)
EXPOSE 1317 26656 26657

COPY entrypoint.sh ./entrypoint.sh
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
