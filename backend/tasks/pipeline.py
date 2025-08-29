import json, asyncio
from .celery_app import celery
from backend.workers.decode import DecodeWorker
from backend.workers.pose import PoseWorker
from backend.workers.features_w import FeaturesWorker
from backend.workers.segment import SegmentWorker
from backend.workers.identify import IdentifyWorker
from backend.workers.indexer import IndexWorker

async def _run_worker(worker_cls, payload, in_topic, out_topic):
    w = worker_cls(worker_cls.__name__.lower(), in_topic, out_topic)
    # monkeypatch: reuse producer/consumer-less handle directly
    return await w.handle(payload)

@celery.task
def run_pipeline(payload: dict):
    # Execute the same pipeline synchronously using the worker logic
    async def _run():
        p = payload
        p = await _run_worker(DecodeWorker, p, 'analysis.requests', 'pose.requests')
        p = await _run_worker(PoseWorker, p, 'pose.requests', 'features.requests')
        p = await _run_worker(FeaturesWorker, p, 'features.requests', 'segment.requests')
        p = await _run_worker(SegmentWorker, p, 'segment.requests', 'identify.requests')
        await _run_worker(IdentifyWorker, p, 'identify.requests', 'index.requests')
        await _run_worker(IndexWorker, p, 'index.requests', None)
    asyncio.run(_run())
    return {"ok": True}
