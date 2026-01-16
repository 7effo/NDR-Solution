#!/bin/bash

set -e

echo "[ThunderX Zeek] Starting Zeek network analysis..."

# Wait for OpenSearch to be available
if [ -n "$OPENSEARCH_HOST" ]; then
    echo "Waiting for OpenSearch at $OPENSEARCH_HOST..."
    until curl -k -u "${OPENSEARCH_USER}:${OPENSEARCH_PASSWORD}" "https://${OPENSEARCH_HOST}/_cluster/health" 2>/dev/null; do
        echo "OpenSearch not ready, waiting..."
        sleep 5
    done
    echo "OpenSearch is ready!"
fi

# Configure Zeek interface
if [ -z "$ZEEK_INTERFACE" ]; then
    echo "ERROR: ZEEK_INTERFACE environment variable not set"
    exit 1
fi

echo "Monitoring interface: $ZEEK_INTERFACE"

# Set interface to promiscuous mode
ip link set "$ZEEK_INTERFACE" promisc on 2>/dev/null || echo "Note: Could not set promiscuous mode (may require host network mode)"

# Start log shipping script in background
if [ -f /usr/local/bin/ship-logs.py ]; then
    python3 /usr/local/bin/ship-logs.py &
fi

# Execute Zeek with provided command or default
exec "$@"
