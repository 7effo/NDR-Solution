# ThunderX Zeek Configuration
# This file defines what scripts to load

@load base/frameworks/cluster
@load base/frameworks/logging
@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http
@load base/protocols/ssl
@load base/protocols/ssh
@load base/protocols/ftp
@load base/protocols/smtp

# File analysis
@load frameworks/files/hash-all-files
@load frameworks/files/extract-all-files

# JSON logging for OpenSearch integration
@load policy/tuning/json-logs

# Custom ThunderX detection scripts
@load ./scripts/thunderx-detections.zeek

# Set cluster configuration based on environment
@if (getenv("ZEEK_CLUSTER_ID") != "")
redef Cluster::default_backend = Cluster::CLUSTER_BACKEND_NATIVE;
@endif

# Configure logging
redef LogAscii::use_json = T;
redef LogAscii::json_timestamps = JSON::TS_ISO8601;

# Increase default connection logging
redef Conn::default_capture_loss_rate = 0.01;

# Set site-specific network
redef Site::local_nets += { 
    10.0.0.0/8,
    172.16.0.0/12,
    192.168.0.0/16
};

# Performance tuning
redef table_expire_interval = 10min;
redef table_expire_delay = 2min;
