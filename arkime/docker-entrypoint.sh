#!/bin/bash

set -e

echo "[ThunderX Arkime] Starting Arkime full packet capture..."

# Wait for OpenSearch
if [ -n "$OPENSEARCH_URL" ]; then
    echo "Waiting for OpenSearch at $OPENSEARCH_URL..."
    until curl -k -u "${OPENSEARCH_USER}:${OPENSEARCH_PASSWORD}" "${OPENSEARCH_URL}/_cluster/health" 2>/dev/null; do
        echo "OpenSearch not ready, waiting..."
        sleep 5
    done
    echo "OpenSearch is ready!"
fi

# Check interface
if [ -z "$ARKIME_INTERFACE" ]; then
    echo "ERROR: ARKIME_INTERFACE environment variable not set"
    exit 1
fi

echo "Capturing on interface: $ARKIME_INTERFACE"

# Initialize Arkime database (only once)
if [ ! -f /data/.arkime_initialized ]; then
    echo "Initializing Arkime database..."
    cd /opt/arkime/db
    ./db.pl --insecure https://${OPENSEARCH_USER}:${OPENSEARCH_PASSWORD}@${OPENSEARCH_URL#https://} init || echo "DB already initialized"
    
    # Create admin user
    if [ -n "$ARKIME_ADMIN_PASSWORD" ]; then
        /opt/arkime/bin/arkime_add_user.sh admin "Admin User" "$ARKIME_ADMIN_PASSWORD" --admin || echo "Admin user may already exist"
    fi
    
    touch /data/.arkime_initialized
fi

# Set interface to promiscuous mode
ip link set "$ARKIME_INTERFACE" promisc on 2>/dev/null || echo "Note: Could not set promiscuous mode"

# Start viewer in background if requested
if [ "$START_VIEWER" = "true" ]; then
    /opt/arkime/bin/viewer -c /data/config/config.ini &
fi

# Execute capture
exec "$@"
