.PHONY: help install test lint format clean build publish act
.DEFAULT_GOAL := help

COLLECTION_PATH = hyperstack/ansible_collections/hyperstack/cloud
PYTHON = uv run

help: ## Show help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "%-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	uv sync --all-extras
	uv add ansible-core

test: ## Run all tests
	cd $(COLLECTION_PATH) && $(PYTHON) pytest tests/unit/ -v --cov=plugins
	cd $(COLLECTION_PATH) && $(PYTHON) ansible-test sanity --python 3.11 --skip-test validate-modules
	cd $(COLLECTION_PATH) && $(PYTHON) ansible-test integration --python 3.11

lint: ## Run linters
	cd $(COLLECTION_PATH) && $(PYTHON) ansible-lint .
	$(PYTHON) yamllint .
	$(PYTHON) black --check hyperstack/
	$(PYTHON) flake8 hyperstack/
	$(PYTHON) pylint hyperstack/
	$(PYTHON) bandit -r hyperstack/

format: ## Format code
	$(PYTHON) black hyperstack/
	$(PYTHON) isort hyperstack/

build: ## Build collection
	cd $(COLLECTION_PATH) && $(PYTHON) ansible-galaxy collection build --force

publish: build ## Publish to Galaxy
	cd $(COLLECTION_PATH) && $(PYTHON) ansible-galaxy collection publish hyperstack-cloud-*.tar.gz --api-key $$GALAXY_API_KEY

clean: ## Clean artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf $(COLLECTION_PATH)/hyperstack-cloud-*.tar.gz .pytest_cache/ .coverage

act: ## Run GitHub workflow with act
	act -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest

ci: lint test build ## Run CI pipeline