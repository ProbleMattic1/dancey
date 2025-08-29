# DanceApp

DanceApp is a demo end‑to‑end system for analyzing uploaded dance videos.  It
contains a **FastAPI** backend, a **Next.js** web frontend and a collection of
Kafka/Celery workers that run the analysis pipeline.  Supporting tooling is
provided for local development (Docker Compose), Kubernetes deployment (Helm
chart) and an optional ML training stack.

The repository is structured as:

| Path | Description |
| ---- | ----------- |
| `backend/` | FastAPI app, database models, Celery tasks and worker implementations. |
| `frontend/` | Next.js client with Tailwind CSS. |
| `infra/` | Local Docker Compose definition for Postgres, Kafka, MinIO, Redis and optional Celery workers. |
| `helm/` | Helm chart for deploying the backend and frontend. |
| `scripts/` | Helper scripts for fetching ML models and running migrations. |
| `tests/` | End‑to‑end test suite. |


## Docker Compose boot with migrations
`make infra-up` (or `docker compose -f infra/docker-compose.yml up -d`) boots
Postgres, Kafka, MinIO and other dependencies.  The backend container waits for
Postgres, runs `alembic upgrade head` automatically, then starts the API.  Use
`make migrate` if you need to apply migrations manually.

## Alembic autogenerate
Database models live under `backend/app/db/models.py`.  To create a new
migration from these SQLAlchemy models run:

```bash
alembic revision --autogenerate -m "your change"
alembic upgrade head
```

## Pose inference with TFLite (optional)
The pose worker loads a default ONNX MoveNet model.  To use the smaller TFLite
variant instead, download a `.tflite` file and set
`POSE_TFLITE_PATH=backend/models/movenet_singlepose_lightning_4.tflite` before
starting the backend or workers.

## Optional Celery pipeline
Kafka is used for asynchronous processing by default.  A synchronous Celery
pipeline is available for environments without Kafka:

1. Start Redis and a Celery worker
   (`docker compose -f infra/docker-compose.yml up -d redis celery`).
2. Set `USE_CELERY=1` on the backend container to enqueue tasks on Celery
   instead of Kafka.

## Helm chart
The chart in `helm/danceapp` deploys both backend and frontend.  Package and
install it by supplying container images for each component:

```bash
helm install danceapp helm/danceapp \
  --set image.backend=<img>,image.frontend=<img>
```

You can customize `values.yaml` to tweak environment variables, replica counts
or to enable a one‑off analysis Job (see below).

## E2E test
A smoke test exercises the entire pipeline against a live stack.  With the
Docker Compose services running locally:

```bash
export E2E=true
pytest tests/test_e2e.py -q
```

## Notifications (Slack/Discord)
`backend/app/common/notify.py` can send webhook notifications when analysis
completes or segments are indexed.  Provide the following environment variables
on the backend service (via Docker Compose or Helm) to enable it:

- `SLACK_WEBHOOK_URL`
- `DISCORD_WEBHOOK_URL`

## Kubernetes Job (Helm)
The Helm chart can launch a one‑off Job that triggers analysis for a specific
video ID:

1. In `helm/danceapp/values.yaml` set:

   ```yaml
   job:
     enabled: true
     videoId: "vid_abc123"
   ```

2. Apply the chart:

   ```bash
   helm upgrade --install danceapp helm/danceapp
   ```

The Job uses the backend image to call the API and queue analysis for
`videoId`.
