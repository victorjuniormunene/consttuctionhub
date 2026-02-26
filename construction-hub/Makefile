# Makefile for Construction Hub Django Project

# Variables
VENV = venv
PYTHON = $(VENV)/Scripts/python
PIP = $(VENV)/Scripts/pip
MANAGE = $(PYTHON) manage.py

# Default target
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  install    - Create virtual environment and install dependencies"
	@echo "  migrate    - Run database migrations"
	@echo "  superuser  - Create a superuser"
	@echo "  run        - Start the development server"
	@echo "  setup      - Full setup: install, migrate, superuser"
	@echo "  clean      - Remove virtual environment and cache files"

# Create virtual environment and install dependencies
.PHONY: install
install:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Run database migrations
.PHONY: migrate
migrate:
	$(MANAGE) migrate

# Create superuser
.PHONY: superuser
superuser:
	$(MANAGE) createsuperuser

# Start development server
.PHONY: run
run:
	$(MANAGE) runserver

# Full setup
.PHONY: setup
setup: install migrate superuser

# Clean up
.PHONY: clean
clean:
	rmdir /s /q $(VENV)
	for /d %%i in (__pycache__) do rmdir /s /q "%%i"
	del /q *.pyc
	del /q db.sqlite3
