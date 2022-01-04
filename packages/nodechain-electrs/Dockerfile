FROM rust:latest AS builder

ARG COMMIT=703c6a20d52b61a234a18812503bd754d448992a

RUN apt-get update
RUN apt-get install -y clang cmake

RUN git clone https://github.com/blockstream/electrs && cd electrs && git checkout ${COMMIT}

WORKDIR /electrs

RUN cargo build --release --bin electrs

FROM debian:stable-slim

WORKDIR /build

COPY --from=builder /electrs/target/release/electrs /build

STOPSIGNAL SIGINT

ENTRYPOINT ["/build/electrs"]