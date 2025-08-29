#!/usr/bin/env bash
set -euo pipefail
echo 'Creating database schema...'
docker compose -f infra/docker-compose.yml exec -T postgres psql -U postgres -d danceapp -v ON_ERROR_STOP=1 < infra/sql/init.sql
echo 'Done.'
