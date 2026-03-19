# Makefile for Quantum Consciousness VAE Project

# Variables
PROJECT_NAME := quantum-consciousness-agi
PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker-compose

# Help target
.PHONY: help
help: ## Display this help message
	@echo "Quantum Consciousness VAE - Makefile Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make [command]"
	@echo ""
	@echo "Commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development setup
.PHONY: setup
setup: ## Set up development environment
	$(PYTHON) -m venv .venv
	.venv/bin/activate && $(PIP) install --upgrade pip
	.venv/bin/activate && $(PIP) install -r requirements.txt
	.venv/bin/activate && $(PIP) install -r requirements-dev.txt

# Run tests
.PHONY: test
test: ## Run all tests
	$(PYTHON) -m pytest tests/ -v

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	$(PYTHON) -m pytest tests/ --cov=quantum_consciousness --cov-report=html --cov-report=term

# Run training
.PHONY: train
train: ## Run model training
	$(PYTHON) train_vae.py

# Run inference
.PHONY: infer
infer: ## Run model inference
	$(PYTHON) inference.py

# Start development environment
.PHONY: dev
dev: ## Start development environment with Docker
	$(DOCKER_COMPOSE) -f docker-compose.yml up -d

# Stop development environment
.PHONY: dev-down
dev-down: ## Stop development environment
	$(DOCKER_COMPOSE) -f docker-compose.yml down

# Start staging environment
.PHONY: stage
stage: ## Start staging environment
	$(DOCKER_COMPOSE) -f docker-compose.staging.yml up -d

# Stop staging environment
.PHONY: stage-down
stage-down: ## Stop staging environment
	$(DOCKER_COMPOSE) -f docker-compose.staging.yml down

# Build Docker images
.PHONY: build
build: ## Build Docker images
	docker build -t $(PROJECT_NAME):latest .

.PHONY: build-dashboard
build-dashboard: ## Build dashboard Docker image
	docker build -f Dockerfile.dashboard -t $(PROJECT_NAME)-dashboard:latest .

# Run security scans
.PHONY: security-scan
security-scan: ## Run security vulnerability scans
	$(PYTHON) -m pip install bandit safety
	bandit -r . -f json -o bandit-report.json
	safety check --json --output safety-report.json

# Clean up
.PHONY: clean
clean: ## Clean up temporary files and directories
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf bandit-report.json
	rm -rf safety-report.json

# Documentation
.PHONY: docs
docs: ## Generate documentation
	$(PYTHON) -m sphinx docs/ docs/_build/

# Linting
.PHONY: lint
lint: ## Run code linting
	$(PYTHON) -m flake8 .
	$(PYTHON) -m black --check .

.PHONY: format
format: ## Format code with Black
	$(PYTHON) -m black .

# Pre-commit hooks
.PHONY: pre-commit
pre-commit: ## Install and run pre-commit hooks
	$(PYTHON) -m pip install pre-commit
	pre-commit install
	pre-commit run --all-files

# Database operations
.PHONY: db-migrate
db-migrate: ## Run database migrations
	$(PYTHON) -m alembic upgrade head

.PHONY: db-reset
db-reset: ## Reset database
	$(PYTHON) -c "from utils.database import reset_database; reset_database()"

# Monitoring
.PHONY: monitor
monitor: ## Start monitoring stack
	$(DOCKER_COMPOSE) -f monitoring/docker-compose.monitoring.yml up -d

.PHONY: monitor-down
monitor-down: ## Stop monitoring stack
	$(DOCKER_COMPOSE) -f monitoring/docker-compose.monitoring.yml down

# Backup operations
.PHONY: backup
backup: ## Create system backup
	mkdir -p backups/
	tar -czf backups/backup-$(shell date +%Y%m%d-%H%M%S).tar.gz \
		--exclude='.venv' \
		--exclude='*.log' \
		--exclude='backups' \
		.

.PHONY: restore
restore: ## Restore from latest backup
	@echo "Restoring from backup..."
	@latest_backup=$$(ls -t backups/backup-*.tar.gz | head -1) && \
	if [ -n "$$latest_backup" ]; then \
		echo "Restoring from $$latest_backup"; \
		tar -xzf "$$latest_backup" -C .; \
	else \
		echo "No backup found"; \
	fi

# System health check
.PHONY: health
health: ## Check system health
	curl -f http://localhost:8000/api/v1/system/health || echo "API service unhealthy"
	curl -f http://localhost:8501/ || echo "Dashboard service unhealthy"

# Update dependencies
.PHONY: update-deps
update-deps: ## Update project dependencies
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt

# Run all checks
.PHONY: check
check: lint test security-scan ## Run all quality checks
	@echo "All checks completed successfully!"

# Release management
.PHONY: release-major
release-major: ## Create major release (1.0.0 -> 2.0.0)
	$(PYTHON) -m bumpversion major

.PHONY: release-minor
release-minor: ## Create minor release (1.0.0 -> 1.1.0)
	$(PYTHON) -m bumpversion minor

.PHONY: release-patch
release-patch: ## Create patch release (1.0.0 -> 1.0.1)
	$(PYTHON) -m bumpversion patch

# Dashboard operations
.PHONY: dashboard
dashboard: ## Start Streamlit dashboard
	streamlit run dashboards/quantum_consciousness_dashboard/app.py

# Quantum hardware operations
.PHONY: quantum-test
quantum-test: ## Test quantum hardware connection
	$(PYTHON) -c "from utils.quantum_test import test_quantum_connection; test_quantum_connection()"

.PHONY: quantum-calibrate
quantum-calibrate: ## Calibrate quantum hardware
	$(PYTHON) -c "from utils.quantum_calibration import calibrate_system; calibrate_system()"

# Performance profiling
.PHONY: profile
profile: ## Profile application performance
	$(PYTHON) -m cProfile -o profile.prof main.py
	$(PYTHON) -m pstats profile.prof

# Generate requirements files
.PHONY: freeze
freeze: ## Generate requirements files from current environment
	$(PIP) freeze > requirements.txt
	$(PIP) freeze > requirements-dev.txt

# Environment setup
.PHONY: env
env: ## Set up environment variables
	cp .env.example .env
	@echo "Environment file created. Please update .env with your values."

# Run all
.PHONY: all
all: setup test build ## Complete setup, test, and build
	@echo "Project setup, testing, and building completed successfully!"