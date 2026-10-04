.PHONY: help install test lint format up down seed scenario clean

help:
	@echo "ThreatGraph X - Command Center"
	@echo "================================"
	@echo "make install      : Install backend & frontend dependencies"
	@echo "make test         : Run full automated pytest suite"
	@echo "make test-unit    : Run fast unit tests"
	@echo "make test-sec     : Run security & RBAC tests"
	@echo "make lint         : Run code linting & type checks"
	@echo "make up           : Launch full stack via Docker Compose"
	@echo "make down         : Stop all container services"
	@echo "make seed         : Seed database with 20,000 synthetic security events"
	@echo "make scenario     : Run multi-stage attack-chain simulation scenario"
	@echo "make clean        : Remove build caches and temporary artifacts"

install:
	cd backend && pip install -e .
	cd frontend && npm install

test:
	cd backend && pytest -v --tb=short

test-unit:
	cd backend && pytest backend/tests/unit/ -v

test-sec:
	cd backend && pytest backend/tests/security/ -v

lint:
	cd backend && flake8 app tests --max-line-length=120 || true
	cd backend && mypy app || true
	cd frontend && npm run lint || true

up:
	docker compose up -d --build

down:
	docker compose down

seed:
	python scripts/seed.py --events 20000

scenario:
	python scripts/run_scenario.py --scenario multi-stage

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf backend/threatgraph_x.db
