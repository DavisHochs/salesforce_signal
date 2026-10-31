# Signal to Send — task runner.
# On Windows, run from Git Bash after installing make (see docs/runbooks/D0.0-local-tooling.md).

ifeq ($(OS),Windows_NT)
  VENV_PY := .venv/Scripts/python.exe
  BOOTSTRAP_PY ?= py -3.12
else
  VENV_PY := .venv/bin/python
  BOOTSTRAP_PY ?= python3.12
endif
PY ?= $(if $(wildcard $(VENV_PY)),$(VENV_PY),python)

.PHONY: help venv install lint format test smoke-jev smoke-sf smoke-mail smoke-all mailpit-up mailpit-down

help:
	@echo "venv        create .venv with Python 3.12"
	@echo "install     install the project and dev tools, set up pre-commit"
	@echo "lint        ruff lint + format check (AUTO)"
	@echo "format      apply ruff formatting and safe fixes"
	@echo "test        run AUTO tests (no live services)"
	@echo "smoke-jev   T0.2 AUTO-LIVE: decision provider returns a valid typed Choice"
	@echo "smoke-sf    T0.3 AUTO-LIVE: authenticate to the org and fetch limits"
	@echo "smoke-mail  T0.4 AUTO-LIVE: message lands in Mailpit (+ chosen service once ADR-003 is accepted)"
	@echo "mailpit-up  start Mailpit in Docker"

venv:
	$(BOOTSTRAP_PY) -m venv .venv

install:
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e ".[dev]"
	$(PY) -m pre_commit install

lint:
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .

format:
	$(PY) -m ruff check --fix .
	$(PY) -m ruff format .

test:
	$(PY) -m pytest -m "not live"

smoke-jev:
	$(PY) -m scripts.smoke.smoke_jev

smoke-sf:
	$(PY) -m scripts.smoke.smoke_sf

smoke-mail:
	$(PY) -m scripts.smoke.smoke_mail

smoke-all: smoke-jev smoke-sf smoke-mail

mailpit-up:
	docker compose up -d mailpit

mailpit-down:
	docker compose down
