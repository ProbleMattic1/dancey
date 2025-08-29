#!/usr/bin/env bash
set -euo pipefail
export DB_DSN="${DB_DSN:-postgresql://postgres:postgres@localhost:5432/danceapp}"
echo "Running Alembic migrations on $DB_DSN"
alembic upgrade head
