#!/bin/bash

# ThunderX NDR - Interactive Installer
# This script guides you through the installation of ThunderX

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
  _____ _                     _          __  __
 |_   _| |__  _   _ _ __   __| | ___ _ _\ \/ /
   | | | '_ \| | | | '_ \ / _` |/ _ \ '__\  / 
   | | | | | | |_| | | | | (_| |  __/ |  /  \ 
   |_| |_| |_|\__,_|_| |_|\__,_|\___|_| /_/\_\
                                               
   Network Detection & Response Platform
   Version 0.1.0-alpha
   
EOF
    echo -e "${NC}"
}

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This installer must be run as root"
        echo "Please run: sudo $0"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check OS
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        log_info "Detected OS: $NAME $VERSION"
    else
        log_warning "Could not detect OS version"
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        echo "Please install Docker first: https://docs.docker.com/engine/install/"
        exit 1
    fi
    
    DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
    log_success "Docker $DOCKER_VERSION detected"
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    COMPOSE_VERSION=$(docker compose version --short)
    log_success "Docker Compose $COMPOSE_VERSION detected"
    
    # Check available memory
    TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $TOTAL_MEM -lt 16 ]]; then
        log_warning "System has ${TOTAL_MEM}GB RAM. Minimum recommended is 16GB for standalone mode"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "System has ${TOTAL_MEM}GB RAM"
    fi
    
    # Check available disk space
    AVAILABLE_DISK=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $AVAILABLE_DISK -lt 500 ]]; then
        log_warning "Available disk space: ${AVAILABLE_DISK}GB. Recommended: 500GB+"
    else
        log_success "Available disk space: ${AVAILABLE_DISK}GB"
    fi
    
    # Check CPU cores
    CPU_CORES=$(nproc)
    if [[ $CPU_CORES -lt 4 ]]; then
        log_warning "System has $CPU_CORES CPU cores. Minimum recommended is 4"
    else
        log_success "System has $CPU_CORES CPU cores"
    fi
}

# Get deployment mode
select_deployment_mode() {
    echo ""
    echo -e "${BLUE}=== Deployment Mode Selection ===${NC}"
    echo ""
    echo "1) Standalone - All components on this host (recommended for getting started)"
    echo "2) Distributed Manager - Management node (OpenSearch, Web UI, API)"
    echo "3) Distributed Sensor - Sensor node (Zeek, Suricata, Arkime)"
    echo ""
    
    while true; do
        read -p "Select deployment mode [1-3]: " mode
        case $mode in
            1)
                DEPLOYMENT_MODE="standalone"
                log_info "Selected: Standalone deployment"
                break
                ;;
            2)
                DEPLOYMENT_MODE="distributed-manager"
                log_info "Selected: Distributed Manager deployment"
                break
                ;;
            3)
                DEPLOYMENT_MODE="distributed-sensor"
                log_info "Selected: Distributed Sensor deployment"
                break
                ;;
            *)
                log_error "Invalid selection. Please choose 1, 2, or 3"
                ;;
        esac
    done
    
    echo "DEPLOYMENT_MODE=$DEPLOYMENT_MODE" >> .env
}

# Configure network interface
configure_network_interface() {
    echo ""
    echo -e "${BLUE}=== Network Interface Configuration ===${NC}"
    echo ""
    
    log_info "Available network interfaces:"
    ip -br link show | grep -v lo | awk '{print "  - " $1}'
    echo ""
    
    read -p "Enter the network interface to monitor (e.g., eth0, ens33): " interface
    
    if ! ip link show "$interface" &> /dev/null; then
        log_error "Interface $interface not found"
        exit 1
    fi
    
    log_success "Using interface: $interface"
    echo "ZEEK_INTERFACE=$interface" >> .env
    echo "SURICATA_INTERFACE=$interface" >> .env
    echo "ARKIME_INTERFACE=$interface" >> .env
    
    # Set promiscuous mode
    log_info "Setting $interface to promiscuous mode..."
    ip link set "$interface" promisc on
    log_success "Promiscuous mode enabled"
}

# Configure credentials
configure_credentials() {
    echo ""
    echo -e "${BLUE}=== Credentials Configuration ===${NC}"
    echo ""
    
    # OpenSearch admin password
    while true; do
        read -s -p "Enter OpenSearch admin password (min 8 chars, uppercase, lowercase, number, special): " os_pass
        echo ""
        read -s -p "Confirm password: " os_pass_confirm
        echo ""
        
        if [[ "$os_pass" != "$os_pass_confirm" ]]; then
            log_error "Passwords do not match"
            continue
        fi
        
        if [[ ${#os_pass} -lt 8 ]]; then
            log_error "Password must be at least 8 characters"
            continue
        fi
        
        # Check password complexity
        if [[ ! "$os_pass" =~ [A-Z] ]] || [[ ! "$os_pass" =~ [a-z] ]] || \
           [[ ! "$os_pass" =~ [0-9] ]] || [[ ! "$os_pass" =~ [^a-zA-Z0-9] ]]; then
            log_error "Password must contain uppercase, lowercase, number, and special character"
            continue
        fi
        
        break
    done
    
    echo "OPENSEARCH_INITIAL_ADMIN_PASSWORD=$os_pass" >> .env
    log_success "OpenSearch admin password set"
    
    # Arkime admin password
    read -s -p "Enter Arkime admin password: " arkime_pass
    echo ""
    echo "ARKIME_ADMIN_PASSWORD=$arkime_pass" >> .env
    
    # PostgreSQL password
    POSTGRES_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    echo "POSTGRES_PASSWORD=$POSTGRES_PASS" >> .env
    
    # API secret key
    API_SECRET=$(openssl rand -hex 32)
    echo "API_SECRET_KEY=$API_SECRET" >> .env
    
    # Web UI session secret
    SESSION_SECRET=$(openssl rand -hex 32)
    echo "WEB_UI_SESSION_SECRET=$SESSION_SECRET" >> .env
    
    log_success "Credentials configured"
}

# Additional configuration for distributed sensor
configure_distributed_sensor() {
    echo ""
    echo -e "${BLUE}=== Distributed Sensor Configuration ===${NC}"
    echo ""
    
    read -p "Enter sensor name (e.g., sensor-01, office-sensor): " sensor_name
    echo "SENSOR_NODE_NAME=$sensor_name" >> .env
    
    read -p "Enter sensor location (e.g., datacenter-1, office-nyc): " sensor_location
    echo "SENSOR_NODE_LOCATION=$sensor_location" >> .env
    
    read -p "Enter manager node IP address: " manager_ip
    echo "MANAGER_NODE_IP=$manager_ip" >> .env
    
    log_success "Distributed sensor configuration complete"
}

# Generate SSL certificates
generate_ssl_certificates() {
    log_info "Generating SSL certificates..."
    
    mkdir -p nginx/ssl opensearch/certs
    
    # Generate OpenSearch certificates
    if [[ ! -f opensearch/certs/ca.pem ]]; then
        openssl req -x509 -newkey rsa:4096 -keyout opensearch/certs/ca-key.pem \
            -out opensearch/certs/ca.pem -days 3650 -nodes \
            -subj "/C=US/ST=State/L=City/O=ThunderX/OU=Security/CN=ThunderX-CA" \
            2>/dev/null
        
        openssl req -newkey rsa:4096 -keyout opensearch/certs/key.pem \
            -out opensearch/certs/cert.csr -nodes \
            -subj "/C=US/ST=State/L=City/O=ThunderX/OU=Security/CN=*.thunderx.local" \
            2>/dev/null
        
        openssl x509 -req -in opensearch/certs/cert.csr -CA opensearch/certs/ca.pem \
            -CAkey opensearch/certs/ca-key.pem -CAcreateserial \
            -out opensearch/certs/cert.pem -days 3650 \
            2>/dev/null
        
        rm opensearch/certs/cert.csr
        chmod 644 opensearch/certs/*.pem
        
        log_success "OpenSearch certificates generated"
    fi
    
    # Generate Nginx certificates
    if [[ ! -f nginx/ssl/cert.pem ]]; then
        openssl req -x509 -newkey rsa:4096 -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem -days 365 -nodes \
            -subj "/C=US/ST=State/L=City/O=ThunderX/CN=thunderx.local" \
            2>/dev/null
        
        chmod 644 nginx/ssl/*.pem
        log_success "Nginx certificates generated"
    fi
}

# Pull Docker images
pull_docker_images() {
    log_info "Pulling Docker images (this may take a while)..."
    
    if [[ "$DEPLOYMENT_MODE" == "standalone" ]]; then
        docker compose pull
    elif [[ "$DEPLOYMENT_MODE" == "distributed-sensor" ]]; then
        docker compose -f docker-compose.distributed.yml pull
    fi
    
    log_success "Docker images pulled"
}

# Build custom Docker images
build_docker_images() {
    log_info "Building custom Docker images (this may take a while)..."
    
    if [[ "$DEPLOYMENT_MODE" == "standalone" ]]; then
        docker compose build --parallel
    elif [[ "$DEPLOYMENT_MODE" == "distributed-sensor" ]]; then
        docker compose -f docker-compose.distributed.yml build --parallel
    fi
    
    log_success "Docker images built"
}

# Initialize services
initialize_services() {
    log_info "Starting ThunderX services..."
    
    if [[ "$DEPLOYMENT_MODE" == "standalone" ]]; then
        docker compose up -d
    elif [[ "$DEPLOYMENT_MODE" == "distributed-sensor" ]]; then
        docker compose -f docker-compose.distributed.yml up -d
    fi
    
    log_success "Services started"
}

# Wait for services to be healthy
wait_for_services() {
    if [[ "$DEPLOYMENT_MODE" != "standalone" ]]; then
        return
    fi
    
    log_info "Waiting for services to become healthy..."
    
    sleep 10
    
    # Wait for OpenSearch
    log_info "Waiting for OpenSearch..."
    for i in {1..30}; do
        if docker exec thunderx-opensearch-node1 curl -k -u "admin:${os_pass}" \
           https://localhost:9200/_cluster/health 2>/dev/null | grep -q "status"; then
            log_success "OpenSearch is ready"
            break
        fi
        sleep 5
    done
    
    # Wait for API Gateway
    log_info "Waiting for API Gateway..."
    for i in {1..30}; do
        if curl -f http://localhost:8080/health 2>/dev/null; then
            log_success "API Gateway is ready"
            break
        fi
        sleep 3
    done
}

# Print completion message
print_completion() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  ThunderX Installation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    if [[ "$DEPLOYMENT_MODE" == "standalone" ]]; then
        echo -e "${BLUE}Access ThunderX:${NC}"
        echo "  Web UI: https://$(hostname -I | awk '{print $1}')"
        echo "  Username: admin"
        echo "  Password: (the password you set during installation)"
        echo ""
        echo -e "${BLUE}OpenSearch Dashboards:${NC}"
        echo "  URL: https://$(hostname -I | awk '{print $1}'):5601"
        echo ""
        echo -e "${BLUE}API Gateway:${NC}"
        echo "  URL: http://$(hostname -I | awk '{print $1}'):8080"
        echo "  Docs: http://$(hostname -I | awk '{print $1}'):8080/docs"
    elif [[ "$DEPLOYMENT_MODE" == "distributed-sensor" ]]; then
        echo -e "${BLUE}Sensor ${sensor_name} configured${NC}"
        echo "  Forwarding to: $manager_ip"
        echo "  Location: $sensor_location"
    fi
    
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Access the web UI and complete initial setup"
    echo "  2. Review the dashboard and verify data ingestion"
    echo "  3. Try the MCP chat: 'Show me network activity'"
    echo "  4. Configure alert rules and notifications"
    echo ""
    echo -e "${BLUE}Documentation:${NC} ./docs/"
    echo -e "${BLUE}Logs:${NC} docker compose logs -f"
    echo -e "${BLUE}Status:${NC} docker compose ps"
    echo ""
}

# Main installation flow
main() {
    print_banner
    check_root
    check_requirements
    
    # Create .env file
    cp .env.example .env 2>/dev/null || true
    
    select_deployment_mode
    
    if [[ "$DEPLOYMENT_MODE" == "standalone" ]] || [[ "$DEPLOYMENT_MODE" == "distributed-sensor" ]]; then
        configure_network_interface
    fi
    
    if [[ "$DEPLOYMENT_MODE" == "standalone" ]] || [[ "$DEPLOYMENT_MODE" == "distributed-manager" ]]; then
        configure_credentials
    fi
    
    if [[ "$DEPLOYMENT_MODE" == "distributed-sensor" ]]; then
        configure_distributed_sensor
    fi
    
    if [[ "$DEPLOYMENT_MODE" == "standalone" ]] || [[ "$DEPLOYMENT_MODE" == "distributed-manager" ]]; then
        generate_ssl_certificates
    fi
    
    # Ask about building images
    echo ""
    read -p "Pull and build Docker images now? (Y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        pull_docker_images
        build_docker_images
        initialize_services
        wait_for_services
    fi
    
    print_completion
}

# Run main installation
main
