#!/bin/bash

set -e

echo "[ThunderX Suricata] Starting Suricata IDS/IPS..."

# Wait for OpenSearch
if [ -n "$OPENSEARCH_HOST" ]; then
    echo "Waiting for OpenSearch at $OPENSEARCH_HOST..."
    until curl -k -u "${OPENSEARCH_USER}:${OPENSEARCH_PASSWORD}" "https://${OPENSEARCH_HOST}/_cluster/health" 2>/dev/null; do
        echo "OpenSearch not ready, waiting..."
        sleep 5
    done
    echo "OpenSearch is ready!"
fi

# Check interface
if [ -z "$SURICATA_INTERFACE" ]; then
    echo "ERROR: SURICATA_INTERFACE environment variable not set"
    exit 1
fi

echo "Monitoring interface: $SURICATA_INTERFACE"

# Update Suricata rules
echo "Updating Suricata rules..."
suricata-update || echo "Warning: Rule update failed, using existing rules"

# Set interface to promiscuous mode
ip link set "$SURICATA_INTERFACE" promisc on 2>/dev/null || echo "Note: Could not set promiscuous mode"

# Start log shipping in background
if [ -f /usr/local/bin/ship-logs.py ]; then
    python3 /usr/local/bin/ship-logs.py &
fi

# Run Suricata
exec "$@"
