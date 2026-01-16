# ThunderX Quick Start Guide

This guide will help you get ThunderX up and running quickly.

## Prerequisites

Before you begin, ensure you have:

- **Linux host** (Ubuntu 22.04+, Debian 12+, or RHEL 9+ recommended)
- **Docker 24.0+** with Docker Compose installed
- **System resources** (minimum for standalone):
  - 16GB RAM
  - 4 CPU cores
  - 500GB available storage
- **Network interface** for packet capture (e.g., eth0, ens33)
- **Root access** (via sudo)

## Quick Installation

### Step 1: Generate SSL Certificates

```bash
cd /home/jix/Thunderx
sudo ./scripts/generate-certs.sh
```

This creates self-signed certificates for OpenSearch and Nginx.

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit the file with your settings
nano .env
```

**Important settings to configure:**
- `OPENSEARCH_INITIAL_ADMIN_PASSWORD` - Strong password (min 8 chars, uppercase, lowercase, number, special char)
- `ARKIME_ADMIN_PASSWORD` - Password for Arkime web interface
- `ZEEK_INTERFACE` - Your network interface (e.g., eth0)
- `SURICATA_INTERFACE` - Same as Zeek interface
- `ARKIME_INTERFACE` - Same as Zeek interface
- `SURICATA_HOME_NET` - Your internal networks (e.g., 192.168.0.0/16)
- `OPENAI_API_KEY` - (Optional) For AI-powered queries

### Step 3: Run Interactive Installer (Recommended)

```bash
sudo ./install.sh
```

The installer will:
1. Check system requirements
2. Prompt for deployment mode (choose **Standalone**)
3. Configure network interface
4. Set credentials
5. Generate certificates (if not done)
6. Build and start all services

**OR** Manual Installation:

### Step 3 (Manual): Build Docker Images

```bash
# Build all images (this takes 10-15 minutes)
docker compose build --parallel
```

### Step 4 (Manual): Start Services

```bash
# Start all services in background
docker compose up -d

# Watch the logs
docker compose logs -f
```

### Step 5: Initialize OpenSearch

Once OpenSearch is running, create index templates:

```bash
# Wait for OpenSearch to be healthy
docker compose ps

# Setup index templates
export OPENSEARCH_PASSWORD="your-opensearch-password"
sudo -E ./scripts/setup-opensearch-templates.sh
```

### Step 6: Access ThunderX

After all services are running (check with `docker compose ps`):

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| **Web UI** | `https://your-host-ip` | admin / (your password) |
| **OpenSearch Dashboards** | `https://your-host-ip/dashboards` | admin / (opensearch password) |
| **API Documentation** | `http://your-host-ip:8080/docs` | Bearer token required |
| **Arkime Viewer** | `https://your-host-ip/arkime` | admin / (arkime password) |

**Note:** You'll get SSL certificate warnings because we're using self-signed certificates. This is normal for development.

## Verification

### Check Service Status

```bash
# View all services
docker compose ps

# All services should show "Up" or "healthy"
```

### Test API

```bash
# Health check
curl http://localhost:8080/health

# Should return: {"status":"healthy","version":"0.1.0-alpha"}
```

### Test MCP AI Query (if OpenAI API key configured)

```bash
# Login to get token
curl -X POST http://localhost:8080/auth/login \
  -d "username=admin&password=your-password"

# Use token for query
curl -X POST http://localhost:8080/query/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me network connections in the last hour"}'
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f zeek
docker compose logs -f suricata
docker compose logs -f mcp-ai-service
```

## Common Issues

### Issue: Services won't start

**Solution:** Check system resources and logs
```bash
# Check Docker resources
docker stats

# Check specific service logs
docker compose logs [service-name]
```

### Issue: Can't capture packets

**Solution:** Ensure interface is in promiscuous mode
```bash
# Check interface
ip link show eth0

# Set promiscuous mode
sudo ip link set eth0 promisc on
```

### Issue: OpenSearch won't start

**Solution:** Increase vm.max_map_count
```bash
sudo sysctl -w vm.max_map_count=262144

# Make permanent
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### Issue: Permission denied errors

**Solution:** Ensure Docker has proper permissions
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Re-login or run
newgrp docker
```

## Next Steps

1. **Configure Dashboards**
   - Access OpenSearch Dashboards
   - Import pre-built visualizations (TODO: create these)
   - Create custom dashboards

2. **Set Up Alerts**
   - Configure alert rules in Suricata
   - Set up notification channels
   - Define alert correlation rules

3. **Threat Intelligence**
   - Configure threat feed API keys in `.env`
   - Enable automatic IOC enrichment

4. **User Management**
   - Create additional users via API
   - Set up role-based access control

5. **Production Hardening**
   - Replace self-signed certificates with proper CA-signed certs
   - Change all default passwords
   - Configure firewall rules
   - Set up backup procedures

## Stopping ThunderX

```bash
# Stop all services
docker compose down

# Stop and remove volumes (CAUTION: deletes all data!)
docker compose down -v
```

## Updating ThunderX

```bash
# Pull latest code
git pull

# Rebuild images
docker compose build --no-cache

# Restart services
docker compose down
docker compose up -d
```

## Getting Help

- **Logs:** `docker compose logs -f`
- **Status:** `docker compose ps`
- **API Docs:** http://localhost:8080/docs
- **OpenSearch Health:** `curl -k -u admin:password https://localhost:9200/_cluster/health`

## Resource Optimization

If running on limited hardware, adjust in `.env`:

```bash
# Reduce memory limits
OPENSEARCH_MEM_LIMIT=4g  # Default is 8g
ZEEK_MEM_LIMIT=1g        # Default is 2g
SURICATA_MEM_LIMIT=1g    # Default is 2g
```

## Security Notes

⚠️ **Important Security Reminders:**

1. Change the default admin password immediately
2. Never expose ThunderX directly to the internet without a firewall
3. Use strong, unique passwords for all services
4. Replace self-signed certificates in production
5. Regularly update Docker images
6. Review and customize Suricata rules for your environment
7. Implement network segmentation
8. Enable audit logging
9. Set up SIEM integration if available
10. Regular backups of configuration and critical data

---

**You're now ready to use ThunderX NDR! 🚀**

For advanced configuration and usage, please refer to the full documentation in `/docs/`.
