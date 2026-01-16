#!/bin/bash

# ThunderX - Dashboard Setup Script
# Configures index patterns and imports dashboards into OpenSearch Dashboards

set -e

OPENSEARCH_DASHBOARDS_URL="http://localhost:5601"
# If using https and self-signed certs from outside the container, we might need -k or proper certs.
# Assuming running from host, addressing localhost:5601.
# Note: docker-compose exposes 5601.

# Credentials - populated from .env if present, otherwise default
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '#' | awk '/=/ {print $1}')
fi

USER="admin"
PASSWORD="${OPENSEARCH_INITIAL_ADMIN_PASSWORD}"

echo "Waiting for OpenSearch Dashboards to be ready..."
until curl -k -s -o /dev/null -u "$USER:$PASSWORD" "$OPENSEARCH_DASHBOARDS_URL/api/status"; do
    echo "Dashboards not ready yet..."
    sleep 5
done

echo "OpenSearch Dashboards is ready."

# Function to create index pattern
create_index_pattern() {
    PATTERN=$1
    TIME_FIELD=$2
    
    echo "Creating index pattern: $PATTERN"
    curl -k -X POST "$OPENSEARCH_DASHBOARDS_URL/api/saved_objects/index-pattern/$PATTERN" \
        -H "osd-xsrf: true" \
        -H "Content-Type: application/json" \
        -u "$USER:$PASSWORD" \
        -d "{
          \"attributes\": {
            \"title\": \"$PATTERN\",
            \"timeFieldName\": \"$TIME_FIELD\"
          }
        }"
    echo ""
}

# Create Index Patterns
create_index_pattern "zeek-*" "@timestamp"
create_index_pattern "suricata-*" "@timestamp"
create_index_pattern "alerts-*" "created_at"

# Import Dashboards
DASHBOARDS_DIR="../dashboards"
if [ -d "$DASHBOARDS_DIR" ]; then
    echo "Importing dashboards from $DASHBOARDS_DIR..."
    for file in "$DASHBOARDS_DIR"/*.ndjson; do
        if [ -f "$file" ]; then
            echo "Importing $file..."
            curl -k -X POST "$OPENSEARCH_DASHBOARDS_URL/api/saved_objects/_import?overwrite=true" \
                -H "osd-xsrf: true" \
                -H "Content-Type: multipart/form-data" \
                -u "$USER:$PASSWORD" \
                -F "file=@$file"
            echo ""
        fi
    done
else
    echo "Dashboards directory not found."
fi

echo "Dashboard setup complete."
