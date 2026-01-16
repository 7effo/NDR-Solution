# Makefile for ThunderX NDR

.PHONY: help build up down restart logs clean certs setup test

help:
	@echo "ThunderX NDR - Make Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make certs       - Generate SSL certificates"
	@echo "  make setup       - Setup OpenSearch templates"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  make build       - Build all Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs        - Tail all logs"
	@echo "  make status      - Show service status"
	@echo ""
	@echo "Development:"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Remove containers and volumes"
	@echo ""

certs:
	@echo "Generating SSL certificates..."
	@./scripts/generate-certs.sh

setup: certs
	@echo "Setting up OpenSearch..."
	@./scripts/setup-opensearch-templates.sh

build:
	@echo "Building Docker images..."
	@docker compose build --parallel

up:
	@echo "Starting ThunderX services..."
	@docker compose up -d
	@echo "Services started. Run 'make logs' to view logs."

down:
	@echo "Stopping ThunderX services..."
	@docker compose down

restart: down up

logs:
	@docker compose logs -f

status:
	@docker compose ps

clean:
	@echo "WARNING: This will remove all containers and volumes!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$$$ ]]; then \
		docker compose down -v; \
		echo "Cleanup complete."; \
	fi

test:
	@echo "Running tests..."
	@# TODO: Implement tests
	@echo "No tests implemented yet."

install: certs build up setup
	@echo "ThunderX installation complete!"
	@echo "Access the web UI at: https://localhost"
