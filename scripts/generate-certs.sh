#!/bin/bash

# Script to generate SSL certificates for ThunderX components
# Run this before starting Docker Compose

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERTS_DIR="$SCRIPT_DIR/../opensearch/certs"
NGINX_SSL_DIR="$SCRIPT_DIR/../nginx/ssl"

echo "Generating SSL certificates for ThunderX..."

# Create directories
mkdir -p "$CERTS_DIR"
mkdir -p "$NGINX_SSL_DIR"

# OpenSearch certificates
echo "Generating OpenSearch certificates..."

if [ ! -f "$CERTS_DIR/ca.pem" ]; then
    # Generate CA
    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout "$CERTS_DIR/ca-key.pem" \
        -out "$CERTS_DIR/ca.pem" \
        -days 3650 \
        -subj "/C=US/ST=State/L=City/O=ThunderX/OU=Security/CN=ThunderX-CA" \
        2>/dev/null
    
    echo "Generated CA certificate"
fi

if [ ! -f "$CERTS_DIR/cert.pem" ]; then
    # Generate node certificate
    openssl req -newkey rsa:4096 -nodes \
        -keyout "$CERTS_DIR/key.pem" \
        -out "$CERTS_DIR/cert.csr" \
        -subj "/C=US/ST=State/L=City/O=ThunderX/OU=Security/CN=*.thunderx.local" \
        2>/dev/null
    
    # Sign with CA
    openssl x509 -req \
        -in "$CERTS_DIR/cert.csr" \
        -CA "$CERTS_DIR/ca.pem" \
        -CAkey "$CERTS_DIR/ca-key.pem" \
        -CAcreateserial \
        -out "$CERTS_DIR/cert.pem" \
        -days 3650 \
        -sha256 \
        2>/dev/null
    
    rm "$CERTS_DIR/cert.csr"
    
    echo "Generated OpenSearch node certificate"
fi

# Admin certificate
if [ ! -f "$CERTS_DIR/admin.pem" ]; then
    openssl req -newkey rsa:4096 -nodes \
        -keyout "$CERTS_DIR/admin-key.pem" \
        -out "$CERTS_DIR/admin.csr" \
        -subj "/C=US/ST=State/L=City/O=ThunderX/OU=Security/CN=admin" \
        2>/dev/null
    
    openssl x509 -req \
        -in "$CERTS_DIR/admin.csr" \
        -CA "$CERTS_DIR/ca.pem" \
        -CAkey "$CERTS_DIR/ca-key.pem" \
        -CAcreateserial \
        -out "$CERTS_DIR/admin.pem" \
        -days 3650 \
        -sha256 \
        2>/dev/null
    
    rm "$CERTS_DIR/admin.csr"
    
    echo "Generated OpenSearch admin certificate"
fi

# Set permissions
chmod 644 "$CERTS_DIR"/*.pem
chmod 600 "$CERTS_DIR"/*-key.pem

# Nginx certificates
echo "Generating Nginx certificates..."

if [ ! -f "$NGINX_SSL_DIR/cert.pem" ]; then
    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout "$NGINX_SSL_DIR/key.pem" \
        -out "$NGINX_SSL_DIR/cert.pem" \
        -days 365 \
        -subj "/C=US/ST=State/L=City/O=ThunderX/CN=thunderx.local" \
        2>/dev/null
    
    chmod 644 "$NGINX_SSL_DIR/cert.pem"
    chmod 600 "$NGINX_SSL_DIR/key.pem"
    
    echo "Generated Nginx certificate"
fi

echo ""
echo "✓ SSL certificates generated successfully!"
echo ""
echo "Locations:"
echo "  OpenSearch: $CERTS_DIR"
echo "  Nginx: $NGINX_SSL_DIR"
echo ""
echo "Note: These are self-signed certificates for development."
echo "For production, replace with proper certificates from a CA."
