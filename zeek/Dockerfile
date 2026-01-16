FROM zeek/zeek:latest

LABEL maintainer="ThunderX Team"
LABEL description="Zeek network analysis framework for ThunderX NDR"

# Install additional dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    jq \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for log shipping
RUN pip3 install --no-cache-dir \
    elasticsearch \
    opensearch-py \
    requests

# Create directories
RUN mkdir -p /var/log/zeek \
    /usr/local/zeek/share/zeek/site/scripts \
    /etc/zeek

# Copy custom Zeek scripts
COPY scripts/*.zeek /usr/local/zeek/share/zeek/site/scripts/
COPY config/local.zeek /usr/local/zeek/share/zeek/site/

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Zeek runs as root to capture packets
USER root

# Set working directory
WORKDIR /var/log/zeek

# Expose ports (if running in non-host mode)
# EXPOSE 47760-47770

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["zeek", "-i", "${ZEEK_INTERFACE}", "local"]
