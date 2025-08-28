# DanceApp — Full Starter Scaffolding

This package bundles a runnable skeleton for the TikTok dance analysis & composer project.

## What’s included
- **backend/** — FastAPI APIs, Kafka orchestrator, event-driven workers (decode, pose, features, segmentation, identify, index), ML modules (features, DTW, labels, dataloader, TCN model & training), PDF exporter.
- **frontend/** — Next.js App Router with upload page, analysis timeline, move library, composer with suggestions.
- **infra/** — docker-compose for Postgres, Kafka/Zookeeper, MinIO (S3), plus a bucket initializer.
- **planning/** — Gantt and Jira backlog Excel files from Section 6.
- **scripts/** — helper scripts to run infra and dev servers.

## Quickstart
1) **Infra** (Kafka, PG, MinIO):
```bash
docker compose -f infra/docker-compose.yml up -d
```
2) **Backend**:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # win: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Start API
uvicorn app.orchestrator.main:app --reload --port 8000
# In new terminals start workers (at least decode→pose→features→segment→identify→index)
python -m workers.decode
python -m workers.pose
python -m workers.features_w
python -m workers.segment
python -m workers.identify
python -m workers.indexer
```
3) **Frontend**:
```bash
cd frontend
npm i
npm run dev
```
Open http://localhost:3000 and upload a small MP4 (the workers are stubs with safe defaults).

## Notes
- Install FFmpeg in your PATH.
- For PyTorch, install the correct CUDA build per your environment.
- MinIO console is on http://localhost:9001 (user: minioadmin / pass: minioadmin); a bucket `bucket` is auto-created.
