FROM jasonish/suricata:latest

LABEL maintainer="ThunderX Team"
LABEL description="Suricata IDS/IPS for ThunderX NDR"

# Install dependencies
# Install dependencies
RUN dnf install -y --allowerasing \
    curl \
    jq \
    && dnf clean all

# Python packages no longer needed as we use Filebeat sidecar

# Create directories
RUN mkdir -p /var/log/suricata \
    /var/lib/suricata/rules \
    /etc/suricata && \
    chmod 777 /var/lib/suricata/rules

# Copy custom configuration
COPY config/suricata.yaml /etc/suricata/

# Copy entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Suricata runs as root
USER root

WORKDIR /var/log/suricata

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["suricata", "-c", "/etc/suricata/suricata.yaml", "-i", "${SURICATA_INTERFACE}"]
