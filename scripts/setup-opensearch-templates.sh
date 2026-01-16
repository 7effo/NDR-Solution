#!/bin/bash

# OpenSearch Index Template Setup Script
# Creates index templates for Zeek, Suricata, and Arkime data

set -e

OPENSEARCH_URL="${OPENSEARCH_URL:-https://localhost:9200}"
OPENSEARCH_USER="${OPENSEARCH_USER:-admin}"
OPENSEARCH_PASSWORD="${OPENSEARCH_PASSWORD}"

if [ -z "$OPENSEARCH_PASSWORD" ]; then
    echo "ERROR: OPENSEARCH_PASSWORD environment variable not set"
    exit 1
fi

echo "Setting up OpenSearch index templates for ThunderX..."

# Wait for OpenSearch to be ready
echo "Waiting for OpenSearch..."
until curl -k -u "${OPENSEARCH_USER}:${OPENSEARCH_PASSWORD}" "${OPENSEARCH_URL}/_cluster/health" 2>/dev/null | grep -q '"status"'; do
    echo "Waiting for OpenSearch to be ready..."
    sleep 5
done

echo "OpenSearch is ready!"

# Create Zeek index template
echo "Creating Zeek index template..."
curl -k -X PUT "${OPENSEARCH_URL}/_index_template/zeek-logs" \
    -u "${OPENSEARCH_USER}:${OPENSEARCH_PASSWORD}" \
    -H 'Content-Type: application/json' \
    -d '{
  "index_patterns": ["zeek-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "5s",
      "index.mapping.total_fields.limit": 2000
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "ts": { "type": "date" },
        "id.orig_h": { "type": "ip" },
        "id.orig_p": { "type": "integer" },
        "id.resp_h": { "type": "ip" },
        "id.resp_p": { "type": "integer" },
        "proto": { "type": "keyword" },
        "service": { "type": "keyword" },
        "duration": { "type": "float" },
        "orig_bytes": { "type": "long" },
        "resp_bytes": { "type": "long" },
        "conn_state": { "type": "keyword" },
        "local_orig": { "type": "boolean" },
        "local_resp": { "type": "boolean" },
        "missed_bytes": { "type": "long" },
        "history": { "type": "keyword" },
        "orig_pkts": { "type": "long" },
        "resp_pkts": { "type": "long" }
      }
    }
  },
  "priority": 100,
  "version": 1
}'

echo ""
echo "Creating Suricata index template..."
curl -k -X PUT "${OPENSEARCH_URL}/_index_template/suricata-logs" \
    -u "${OPENSEARCH_USER}:${OPENSEARCH_PASSWORD}" \
    -H 'Content-Type: application/json' \
    -d '{
  "index_patterns": ["suricata-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "5s",
      "index.mapping.total_fields.limit": 2000
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "timestamp": { "type": "date" },
        "event_type": { "type": "keyword" },
        "src_ip": { "type": "ip" },
        "src_port": { "type": "integer" },
        "dest_ip": { "type": "ip" },
        "dest_port": { "type": "integer" },
        "proto": { "type": "keyword" },
        "alert": {
          "properties": {
            "signature": { "type": "text" },
            "signature_id": { "type": "integer" },
            "category": { "type": "keyword" },
            "severity": { "type": "integer" },
            "action": { "type": "keyword" }
          }
        },
        "flow": {
          "properties": {
            "pkts_toserver": { "type": "long" },
            "pkts_toclient": { "type": "long" },
            "bytes_toserver": { "type": "long" },
            "bytes_toclient": { "type": "long" }
          }
        }
      }
    }
  },
  "priority": 100,
  "version": 1
}'

echo ""
echo "Creating Arkime index template..."
curl -k -X PUT "${OPENSEARCH_URL}/_index_template/arkime-sessions" \
    -u "${OPENSEARCH_USER}:${OPENSEARCH_PASSWORD}" \
    -H 'Content-Type: application/json' \
    -d '{
  "index_patterns": ["arkime_sessions3-*"],
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "10s"
    },
    "mappings": {
      "properties": {
        "firstPacket": { "type": "date" },
        "lastPacket": { "type": "date" },
        "ipProtocol": { "type": "integer" },
        "srcIp": { "type": "ip" },
        "dstIp": { "type": "ip" },
        "srcPort": { "type": "integer" },
        "dstPort": { "type": "integer" },
        "srcBytes": { "type": "long" },
        "dstBytes": { "type": "long" },
        "srcPackets": { "type": "long" },
        "dstPackets": { "type": "long" },
        "node": { "type": "keyword" }
      }
    }
  },
  "priority": 100,
  "version": 1
}'

echo ""
echo "✓ Index templates created successfully!"
echo ""
echo "Creating ISM policies for data retention..."

# Create ISM policy for log rotation
curl -k -X PUT "${OPENSEARCH_URL}/_plugins/_ism/policies/log_retention" \
    -u "${OPENSEARCH_USER}:${OPENSEARCH_PASSWORD}" \
    -H 'Content-Type: application/json' \
    -d '{
  "policy": {
    "description": "Delete old logs after retention period",
    "default_state": "hot",
    "states": [
      {
        "name": "hot",
        "actions": [],
        "transitions": [
          {
            "state_name": "delete",
            "conditions": {
              "min_index_age": "30d"
            }
          }
        ]
      },
      {
        "name": "delete",
        "actions": [
          {
            "delete": {}
          }
        ],
        "transitions": []
      }
    ],
    "ism_template": {
      "index_patterns": ["zeek-*", "suricata-*"],
      "priority": 100
    }
  }
}'

echo ""
echo "✓ ISM policies created successfully!"
echo ""
echo "OpenSearch setup complete!"
