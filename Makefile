SHELL := /bin/bash

.PHONY: infra-up infra-down migrate backend workers frontend gen-api openapi

infra-up:
	docker compose -f infra/docker-compose.yml up -d

infra-down:
	docker compose -f infra/docker-compose.yml down -v

migrate:
	./scripts/migrate.sh

backend:
	uvicorn backend.app.orchestrator.main:app --reload

workers:
	python -m backend.workers.decode & \
	python -m backend.workers.pose & \
	python -m backend.workers.features_w & \
	python -m backend.workers.segment & \
	python -m backend.workers.identify & \
	python -m backend.workers.indexer

frontend:
	cd frontend && npm i && npm run dev

gen-api:
	cd frontend && npm i && npm run gen:api

openapi:
	python scripts/export_openapi.py
