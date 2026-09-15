.PHONY: install dev test lint build

install:
	python -m pip install -r backend/requirements-dev.txt
	npm ci --prefix frontend

dev:
	docker compose up --build

test:
	cd backend && pytest -q

lint:
	cd backend && ruff check app tests
	npm run lint --prefix frontend

build:
	npm run build --prefix frontend
