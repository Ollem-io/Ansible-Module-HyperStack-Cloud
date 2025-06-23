.PHONY: help install test lint format clean build publish
.DEFAULT_GOAL := help

COLLECTION_PATH = hyperstack/ansible_collections/hyperstack/cloud
PYTHON_VERSION = 3.11

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	@echo "Installing dependencies with uv..."
	uv sync --all-extras
	uv run pip install ansible-core

test: ## Run all tests
	@echo "Running unit tests..."
	cd $(COLLECTION_PATH) && uv run python -m pytest tests/unit/ -v --cov=plugins --cov-report=term-missing
	@echo "Running sanity tests..."
	cd $(COLLECTION_PATH) && uv run ansible-test sanity --python $(PYTHON_VERSION) --skip-test validate-modules
	@echo "Running integration tests..."
	cd $(COLLECTION_PATH) && uv run ansible-test integration --python $(PYTHON_VERSION)

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	cd $(COLLECTION_PATH) && uv run python -m pytest tests/unit/ -v --cov=plugins --cov-report=term-missing

test-sanity: ## Run sanity tests only
	@echo "Running sanity tests..."
	cd $(COLLECTION_PATH) && uv run ansible-test sanity --python $(PYTHON_VERSION) --skip-test validate-modules

test-integration: ## Run integration tests only
	@echo "Running integration tests..."
	cd $(COLLECTION_PATH) && uv run ansible-test integration --python $(PYTHON_VERSION)

lint: ## Run linting tools
	@echo "Running ansible-lint..."
	cd $(COLLECTION_PATH) && uv run ansible-lint .
	@echo "Running yamllint..."
	cd $(COLLECTION_PATH) && uv run yamllint .
	@echo "Running Python linting..."
	uv run black --check hyperstack/
	uv run flake8 hyperstack/
	uv run pylint hyperstack/
	@echo "Running security scan..."
	uv run bandit -r hyperstack/
	uv run safety check

format: ## Format code
	@echo "Formatting Python code..."
	uv run black hyperstack/
	uv run isort hyperstack/

security: ## Run security checks
	@echo "Running security scan..."
	uv run bandit -r hyperstack/
	uv run safety check

type-check: ## Run type checking
	@echo "Running type checking..."
	uv run mypy hyperstack/

build: ## Build collection
	@echo "Building collection..."
	cd $(COLLECTION_PATH) && uv run ansible-galaxy collection build --force
	@echo "Collection built successfully!"
	@ls -la $(COLLECTION_PATH)/hyperstack-cloud-*.tar.gz

install-collection: build ## Install built collection locally
	@echo "Installing collection locally..."
	cd $(COLLECTION_PATH) && uv run ansible-galaxy collection install hyperstack-cloud-*.tar.gz --force
	@echo "Testing installed collection..."
	uv run ansible-doc hyperstack.cloud.cloud_manager

publish: build ## Publish collection to Ansible Galaxy
	@echo "Publishing collection to Ansible Galaxy..."
	@if [ -z "$$GALAXY_API_KEY" ]; then \
		echo "Error: GALAXY_API_KEY environment variable not set"; \
		exit 1; \
	fi
	cd $(COLLECTION_PATH) && uv run ansible-galaxy collection publish hyperstack-cloud-*.tar.gz --api-key $$GALAXY_API_KEY

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name "*.retry" -delete
	rm -rf $(COLLECTION_PATH)/hyperstack-cloud-*.tar.gz
	rm -rf $(COLLECTION_PATH)/tests/output/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	@echo "Clean complete!"

docs: ## Generate documentation
	@echo "Generating documentation..."
	cd $(COLLECTION_PATH) && uv run ansible-doc hyperstack.cloud.cloud_manager

validate: ## Validate collection structure
	@echo "Validating collection structure..."
	cd $(COLLECTION_PATH) && uv run ansible-galaxy collection build --force
	cd $(COLLECTION_PATH) && uv run ansible-galaxy collection install hyperstack-cloud-*.tar.gz --force
	@echo "Collection validation complete!"

dev-setup: install ## Setup development environment
	@echo "Setting up development environment..."
	uv run pre-commit install
	@echo "Development environment ready!"

ci: lint test build ## Run CI pipeline locally
	@echo "CI pipeline completed successfully!"

ci-local: ## Run CI pipeline locally with AMD64 enforcement (Docker-based)
	@echo "Running CI pipeline locally with AMD64 enforcement..."
	@echo "Setting up Python 3.11 environment..."
	uv python install 3.11
	uv sync --all-extras
	uv run pip install ansible-core
	@echo ""
	@echo "=== Running Lint Stage ==="
	@cd $(COLLECTION_PATH) && uv run ansible-lint .
	@cd $(COLLECTION_PATH) && uv run yamllint .
	@uv run black --check hyperstack/
	@uv run flake8 hyperstack/
	@uv run pylint hyperstack/
	@uv run bandit -r hyperstack/
	@uv run safety check
	@echo ""
	@echo "=== Running Test Stage (Python 3.9 + Ansible 2.14) ==="
	@uv python install 3.9
	@uv sync --all-extras
	@uv run pip install "ansible-core>=2.14.0,<2.14.99"
	@cd $(COLLECTION_PATH) && uv run python -m pytest tests/unit/ -v --cov=plugins --cov-report=xml
	@cd $(COLLECTION_PATH) && uv run ansible-test sanity --python 3.9 --skip-test validate-modules
	@echo ""
	@echo "=== Running Test Stage (Python 3.9 + Ansible 2.17) ==="
	@uv run pip install "ansible-core>=2.17.0,<2.17.99"
	@cd $(COLLECTION_PATH) && uv run python -m pytest tests/unit/ -v --cov=plugins --cov-report=xml
	@cd $(COLLECTION_PATH) && uv run ansible-test sanity --python 3.9 --skip-test validate-modules
	@echo ""
	@echo "=== Running Test Stage (Python 3.11 + Ansible 2.14) ==="
	@uv python install 3.11
	@uv sync --all-extras
	@uv run pip install "ansible-core>=2.14.0,<2.14.99"
	@cd $(COLLECTION_PATH) && uv run python -m pytest tests/unit/ -v --cov=plugins --cov-report=xml
	@cd $(COLLECTION_PATH) && uv run ansible-test sanity --python 3.11 --skip-test validate-modules
	@echo ""
	@echo "=== Running Test Stage (Python 3.11 + Ansible 2.17) ==="
	@uv run pip install "ansible-core>=2.17.0,<2.17.99"
	@cd $(COLLECTION_PATH) && uv run python -m pytest tests/unit/ -v --cov=plugins --cov-report=xml
	@cd $(COLLECTION_PATH) && uv run ansible-test sanity --python 3.11 --skip-test validate-modules
	@echo ""
	@echo "=== Running Integration Tests ==="
	@cd $(COLLECTION_PATH) && uv run ansible-test integration --python 3.11 --coverage
	@cd $(COLLECTION_PATH) && uv run ansible-test coverage report --all --omit-files='*/test_*'
	@echo ""
	@echo "=== Building Collection ==="
	@cd $(COLLECTION_PATH) && uv run ansible-galaxy collection build --force
	@cd $(COLLECTION_PATH) && uv run ansible-galaxy collection install hyperstack-cloud-*.tar.gz --force
	@uv run ansible-doc hyperstack.cloud.cloud_manager
	@echo ""
	@echo "Local CI pipeline with AMD64 enforcement completed successfully!"

ci-local-docker: ## Run CI pipeline in Docker with AMD64 platform enforcement
	@echo "Running CI pipeline in Docker with AMD64 platform enforcement..."
	@docker run --rm -it \
		--platform linux/amd64 \
		-v $(PWD):/workspace \
		-w /workspace \
		python:3.11-slim-bullseye \
		/bin/bash -c " \
			apt-get update && apt-get install -y git curl && \
			curl -LsSf https://astral.sh/uv/install.sh | sh && \
			export PATH=\"/root/.cargo/bin:\$$PATH\" && \
			uv sync --all-extras && \
			uv run pip install ansible-core && \
			make ci \
		"

all: clean install lint test build ## Run complete workflow
	@echo "Complete workflow finished!"