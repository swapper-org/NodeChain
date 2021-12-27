FROM ubuntu:latest
# Create a user if required
RUN useradd -r monero
# Setup and cleanup of the packages required
RUN  apt-get update \
  && apt-get install -y curl \
  && rm -rf /var/lib/apt/lists/*
# Declare the environment variables (version, path, data-dir etc)
ENV MONERO_VERSION=0.17.3.0
ENV MONERO_SHA256=ac18ce3d1189410a5c175984827d5d601974733303411f6142296d647f6582ce
ENV MONERO_DATA=/home/monero/.bitmonero
# Get the compiled binaries and extract them
RUN curl https://dlsrc.getmonero.org/cli/monero-linux-x64-v$MONERO_VERSION.tar.bz2 -O &&\
  echo "$MONERO_SHA256  monero-linux-x64-v$MONERO_VERSION.tar.bz2" | sha256sum -c - &&\
  tar -xvf monero-linux-x64-v$MONERO_VERSION.tar.bz2 -C /opt
# RUN wget https://dlsrc.getmonero.org/cli/monero-linux-x64-v${MONERO_VERSION}.tar.bz2
# RUN tar -xf *.tar.bz2 -C /opt
# Cleanup the workspace
RUN rm *.tar.bz2
# Append the bin folder to the %PATH%
ENV PATH=/opt/monero-x86_64-linux-gnu-v${MONERO_VERSION}:$PATH
# Mount volume
VOLUME ["/home/monero/.bitmonero"]
# Expose required ports (both testnet & mainnet)
EXPOSE 18088 28088 38088
# Copy wallet directory
COPY /wallet-dir /wallet-dir
# Copy and define the entrypoint
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["sh", "/entrypoint.sh"]
# Define the default command
CMD ["monero-wallet-rpc"]