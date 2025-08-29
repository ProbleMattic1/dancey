# DanceApp

DanceApp is a demo end‑to‑end system for analyzing uploaded dance videos.  It
contains a **FastAPI** backend, a **Next.js** web frontend and a collection of
Kafka/Celery workers that run the analysis pipeline.  Supporting tooling is
provided for local development (Docker Compose), Kubernetes deployment (Helm
chart) and an optional ML training stack.

## Project Plan Summary
The repository was bootstrapped from an extensive ChatGPT planning session.
The full transcript is available in [`DanceyChatGPT.md`](DanceyChatGPT.md).
Major steps from that plan are summarized below:

1. **Vision, Scope & Constraints** – Detect dance moves in short videos and
   let users compose dances; MVP targets single-dancer uploads, 2D pose
   extraction, heuristic segmentation, and a small move taxonomy.
2. **Move Taxonomy & Labeling** – Define a hierarchical move ontology, provide
   exemplars and annotation guidelines, and version the taxonomy with tools
   like CVAT or Label Studio.
3. **Computer Vision & ML** – Use MoveNet/BlazePose for keypoints, smooth and
   normalize poses, segment motion via energy/change-point detection, and
   identify moves through template matching or learned classifiers.
4. **Data Pipeline & Infrastructure** – Ingest uploads to object storage,
   process them through GPU workers (pose → features → segmentation →
   identification), and store results in Postgres with optional search and
   caching layers.
5. **Backend Services & Data Model** – FastAPI endpoints handle uploads,
   analysis jobs, taxonomy CRUD, search, and dance composition, backed by
   tables for users, videos, segments, moves, and compositions.
6. **Web App & UX** – Next.js frontend offers upload/analysis status, move
   index pages, and a drag‑and‑drop composer for assembling new dances.
7. **Quality & Human‑in‑the‑Loop** – Track metrics like IoU and
   precision/recall, surface low‑confidence segments for annotation, and allow
   user corrections to improve models.
8. **Safety & Compliance** – Respect content rights, handle takedowns, enforce
   privacy policies, and filter sensitive content.
9. **Scalability & Performance** – Target ~60–120 videos per GPU hour, aim for
   analysis latency under twice the clip length, and use quantized models and
   batching to control cost.
10. **Roadmap** – Phase 0 foundations, Phase 1 MVP analysis, Phase 2 learned
    identification, Phase 3 composer & sharing, and Phase 4 robustness &
    scale.
11. **Data & Model Training** – Collect consented clips, augment data,
    train TCN/Transformer models on joint features, and version datasets and
    models with tools like DVC and MLflow.
12. **Edge Cases & Heuristics** – Handle cuts, tempo shifts, occlusion, mirror
    detection, and non‑dance segments.
13. **Security & Reliability** – Perform AV scanning, rate limiting, backups,
    audit logging, and maintain clear job state transitions.
14. **Team, Budget & Deliverables** – Outline required roles, monthly cost
    estimates, and an MVP checklist (taxonomy, analysis pipeline, move index,
    composer, quality dashboard, and rights workflow).
15. **Initial Execution Steps** – Week‑one tasks include spinning up repos,
    implementing pose extraction and heuristic segmentation, drafting taxonomy
    v0.1, building a minimal upload UI, annotating sample clips, and writing
    policies.
16. **Implementation Blueprints** – Subsequent sections of the transcript
    provide deeper guidance for API contracts, queue/message schemas, storage
    layout, feature vectors, segmentation parameters, classifier
    architectures, data versioning, security considerations, testing
    strategy, and runnable worker skeletons.
17. **Composer Intelligence & Exporters** – Later planning covers a
    choreography graph, Markov‑based move suggestions, beat alignment and
    retargeting, plus exporters like PDF tutorial sheets and JSON schemas for
    external tools.

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

  <<<<<<< codex/expand-project-details-in-readme-95kbki
  ### Implementation Blueprint Highlights

  - **API Contracts** – FastAPI endpoints manage uploads, taxonomy CRUD, segment
    search and composition editing with Pydantic request/response models.
  - **Message Schemas & Queues** – Kafka topics (or Celery tasks) carry typed
    messages through decode → pose → features → segment → identify → index stages.
  - **Storage Layout** – Raw uploads and derived clips live in object storage
    (MinIO/S3); metadata and segment records reside in Postgres.
  - **Feature Vectors & Segmentation** – Normalized joint coordinates and motion
    energy feed change‑point detectors that split videos into candidate move
    segments.
  - **Classifier Architectures** – Early prototypes rely on template matching; the
    roadmap evolves toward TCN or Transformer classifiers with calibration.
  - **Data Versioning & Reproducibility** – Dataset manifests and model artifacts
    are tracked with DVC and MLflow; runs log random seeds and environment hashes.
  - **Security & Privacy** – Uploads undergo AV scanning and consent checks, with
    audit logs for access and deletions.
  - **Testing Strategy** – Unit tests cover workers and API routes, while an E2E
    smoke test validates the full pipeline against a sample clip.
  - **Worker Skeletons** – DecodeWorker, PoseWorker, FeaturesWorker, SegmentWorker,
    IdentifyWorker and IndexWorker provide extensible entry points for each stage.

  ### Composer Intelligence & Exporters

  - **Choreography Graph** – Sequence data produces move statistics and transition
    probabilities that inform suggestions.
  - **Markov Suggestion Engine** – A backoff model blends trigram, bigram and
    unigram counts with temperature‑scaled sampling and optional difficulty
    constraints.
  - **Beat Alignment & Retargeting** – Durations are normalized to beats and can be
    stretched or mirrored to match a new song’s tempo or camera angle.
  - **Export Formats** – Planned outputs include PDF step sheets, JSON definitions
    and future auto‑rendered tutorial videos.

  ### Operational Enhancements

  - **Notifications** – Slack/Discord webhook helpers announce when identification
    and indexing jobs complete.
  - **Optional ORM** – Workers can switch between async SQLAlchemy models and raw
    SQL for database access.
  - **Kubernetes Job Template** – Helm chart includes a one‑off job for triggering
    analysis of a specific video via the API.

  These notes capture the intent and methodology behind the generated codebase
  and serve as a guide for future development.

  Last updated: Fri Aug 29 04:06:42 UTC 2025
  =======
    Last updated: Fri Aug 29 03:58:08 UTC 2025
    =======
    Last updated: Fri Aug 29 03:54:11 UTC 2025
    >>>>>>> main
  >>>>>>> main
