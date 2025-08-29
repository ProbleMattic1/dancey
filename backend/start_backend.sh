#!/usr/bin/env bash
set -euo pipefail
echo "[backend] Waiting for Postgres at ${DB_DSN:-postgresql://postgres:postgres@postgres:5432/danceapp} ..."
python - <<'PY'
import asyncio, os, sys
import asyncpg
dsn = os.getenv("DB_DSN","postgresql://postgres:postgres@postgres:5432/danceapp")
async def main():
    for i in range(60):
        try:
            con = await asyncpg.connect(dsn=dsn)
            await con.close()
            print("DB reachable")
            return
        except Exception as e:
            print("wait db...", e)
            await asyncio.sleep(2)
    sys.exit(1)
asyncio.run(main())
PY
echo "[backend] Running Alembic migrations..."
alembic upgrade head || true
echo "[backend] Starting API server..."
exec uvicorn backend.app.orchestrator.main:app --host 0.0.0.0 --port 8000
