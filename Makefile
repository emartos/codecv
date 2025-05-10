# ========================================
# Makefile for Python environment setup,
# running the app, and various utilities
# ========================================

# ====================
# Variables
# ====================
PYTHON := venv/bin/python
PIP := venv/bin/pip
FLAKE8 := venv/bin/flake8
PRE_COMMIT := venv/bin/pre-commit
ENV_FILE := .env
VENV := venv
VENV_EXISTS := $(shell [ -d "$(VENV)/bin" ] && echo 1 || echo 0)
pattern ?= llm:prompt**

# Colors for messages
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

# ====================
# Load environment variables
# ====================
ifneq (,$(wildcard .env))
    include .env
    export $(shell sed 's/=.*//g' .env)
endif

# ====================
# PHONY Targets
# ====================
.PHONY: help env venv check-venv create-venv install delete-venv \
	install-requirements run freeze-requirements lint pre-commit \
	clean cache-list cache-clear app-version

# ====================
# Help Utilities
# ====================

# Target: help - Displays available commands with their descriptions and parameters
help:
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -B 1 -E '^[a-zA-Z0-9._-]+:' Makefile | \
	grep -v '^--' | \
	grep -v '^.PHONY:' | \
	awk '/^# Target: / {split(substr($$0, 10), a, " - "); desc=a[2]; next} /^[^#]/ {print substr($$0, 1, length($$0)-1) ": " desc}'

# Target: env - Creates .env file if it doesn't exist
env:
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "$(YELLOW)Creating .env file from template...$(NC)"; \
		cp $(ENV_FILE).template $(ENV_FILE); \
		echo "$(GREEN)Created $(ENV_FILE) - Please update with your settings$(NC)"; \
	fi

# ====================
# Environment Setup / Dependencies
# ====================

# Target: check-venv - Checks if the virtual environment exists
check-venv:
	@if [ "$(VENV_EXISTS)" = "0" ]; then \
		echo "$(RED)Error: Virtual environment not found. Please run 'make create-venv' first.$(NC)"; \
		exit 1; \
	fi

# Target: create-venv - Creates a virtual environment if it doesn't exist
create-venv:
	@if [ "$(VENV_EXISTS)" = "0" ]; then \
		echo "$(YELLOW)Creating virtual environment...$(NC)"; \
		python3 -m venv $(VENV); \
	fi

# Target: delete-venv - Deletes the virtual environment
delete-venv:
	@echo "$(YELLOW)Deleting the virtual environment...$(NC)"
	@rm -rf $(VENV)

# Target: install-requirements - Installs dependencies from requirements.txt
install-requirements: check-venv
	@echo "$(GREEN)Installing requirements from code/requirements.txt...$(NC)"
	@$(PIP) install -r code/requirements.txt

# Target: freeze-requirements - Freezes dependencies into requirements.txt
freeze-requirements: check-venv
	@echo "$(GREEN)Freezing requirements in code/requirements.txt...$(NC)"
	@$(PIP) freeze > code/requirements.txt

# ====================
# Code Analysis and Pre-commit Hooks
# ====================

# Target: lint - Runs flake8 linting on the codebase
lint:
	@echo "$(GREEN)Running flake8 linting...$(NC)"
	@$(FLAKE8) code

# Target: pre-commit - Runs configured pre-commit hooks
pre-commit: check-venv
	@echo "$(GREEN)Running pre-commit hooks...$(NC)"
	@$(PRE_COMMIT) run --files $(shell find code -type f -name '*.py')

# Target: pre-commit-force - Runs configured pre-commit hooks with force option
pre-commit-force: check-venv
	@echo "$(GREEN)Running pre-commit hooks...$(NC)"
	@$(PRE_COMMIT) run --all-files

# ====================
# Execution and Development
# ====================

# Target: app-version - Prints the current version of the program
app-version: check-venv
	@echo "$(GREEN)Version of the program:$(NC)"
	@$(PYTHON) -c "from code.version import __version__; print(__version__)"

# Target: run - Runs the main application
run: check-venv
	@echo "$(GREEN)Running the application...$(NC)"
	@$(PYTHON) code/app.py

# ====================
# Cleaning and Maintenance
# ====================

# Target: clean - Removes temporary files
clean:
	@echo "$(GREEN)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +

# ====================
# Cache / Redis
# ====================

# Target: cache-list - Displays cache keys matching a pattern
cache-list:
	@$(PYTHON) ./code/scripts/cache.py "list" "$(pattern)"

# Target: cache-clear - Clears cache keys matching a pattern
cache-clear:
	@$(PYTHON) ./code/scripts/cache.py "invalidate" "$(pattern)"
