FROM ubuntu:22.04

LABEL maintainer="ThunderX Team"
LABEL description="Arkime (Moloch) full packet capture for ThunderX NDR"

ENV DEBIAN_FRONTEND=noninteractive
ENV ARKIME_VERSION=5.0.1

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    sudo \
    ethtool \
    libjson-perl \
    libwww-perl \
    libpcap0.8 \
    libpcap-dev \
    python3 \
    python3-pip \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Download and install Arkime
RUN cd /tmp && \
    wget https://github.com/arkime/arkime/releases/download/v${ARKIME_VERSION}/arkime_${ARKIME_VERSION}-1.ubuntu2204_amd64.deb && \
    dpkg -i arkime_${ARKIME_VERSION}-1.ubuntu2204_amd64.deb || apt-get install -f -y && \
    rm arkime_${ARKIME_VERSION}-1.ubuntu2204_amd64.deb

# Create directories
RUN mkdir -p /data/pcap /data/logs /data/config

# Copy configuration
COPY config/config.ini /data/config/config.ini

# Copy entrypoint
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Arkime runs as root for packet capture
USER root

WORKDIR /data

# Viewer port
EXPOSE 8005

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/opt/arkime/bin/capture", "-c", "/data/config/config.ini"]
