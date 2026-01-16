# Zeek custom scripts for ThunderX NDR
# Load these scripts in local.zeek

@load base/frameworks/notice
@load base/protocols/conn
@load base/protocols/dns
@load base/protocols/http
@load base/protocols/ssl
@load policy/frameworks/files/detect-MHR

# JSON logging for easy integration with OpenSearch
@load policy/tuning/json-logs.zeek

module ThunderX;

export {
    # Define the Log ID
    redef enum Log::ID += { LOG };

    redef enum Notice::Type += {
        ## Indicates suspicious DNS activity
        Suspicious_DNS_Query,
        ## Indicates potential data exfiltration
        Potential_Data_Exfil,
        ## Indicates connection to known bad IP
        Connection_To_Bad_IP,
        ## Indicates port scanning behavior
        Port_Scan_Detected,
        ## Indicates weak SSL/TLS usage
        Suspicious_SSL_Conn,
    };
}

# Log all notices to OpenSearch-friendly format
event zeek_init() {
    Log::create_stream(ThunderX::LOG, [$columns=Notice::Info, $path="thunderx-notices"]);
    print "ThunderX Zeek Detections Loaded";
}

# Suspicious DNS detection
event dns_request(c: connection, msg: dns_msg, query: string, qtype: count, qclass: count) {
    # Check for DNS tunneling indicators
    if (|query| > 50) {
        NOTICE([$note=Suspicious_DNS_Query,
                $msg=fmt("Suspiciously long DNS query: %s", query),
                $conn=c,
                $identifier=cat(c$id$orig_h, query)]);
    }
    
    # Check for queries to newly registered domains (implement with threat intel)
    # TODO: Integration with threat intel feeds
}

# Large data transfer detection
event connection_state_remove(c: connection) {
    local orig_bytes = c$orig$size;
    local resp_bytes = c$resp$size;
    local total_bytes = orig_bytes + resp_bytes;
    
    # Alert on large transfers (> 1GB)
    if (total_bytes > 1073741824) {
        NOTICE([$note=Potential_Data_Exfil,
                $msg=fmt("Large data transfer detected: %d bytes", total_bytes),
                $conn=c,
                $identifier=cat(c$id$orig_h, c$id$resp_h)]);
    }
}

# Basic port scanning detection
global scan_threshold = 20;
global scanner_ips: table[addr] of set[port] &create_expire=5min;

event connection_attempt(c: connection) {
    local orig = c$id$orig_h;
    local port = c$id$resp_p;
    
    if (orig !in scanner_ips) {
        scanner_ips[orig] = set();
    }
    
    add scanner_ips[orig][port];
    
    if (|scanner_ips[orig]| > scan_threshold) {
        NOTICE([$note=Port_Scan_Detected,
                $msg=fmt("Port scan detected from %s (%d ports)", orig, |scanner_ips[orig]|),
                $src=orig,
                $identifier=cat(orig)]);
    }
}

# SSL/TLS weak cipher detection
event ssl_established(c: connection) {
    local cipher = c$ssl$cipher;
    
    # Check for weak ciphers
    if (/RC4/ in cipher || /MD5/ in cipher || /DES/ in cipher) {
        NOTICE([$note=Suspicious_SSL_Conn,
                $msg=fmt("Weak SSL cipher detected: %s", cipher),
                $conn=c]);
    }
}
