import json, os, time
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from aiokafka import AIOKafkaProducer
from dotenv import load_dotenv

load_dotenv()
KAFKA_BOOT = os.getenv("KAFKA_BOOT","localhost:9092")

app = FastAPI(title="DanceApp API")
producer: AIOKafkaProducer | None = None

def nowiso(): return datetime.now(timezone.utc).isoformat()

class AnalysisRequest(BaseModel):
    video_id: str
    model_version: str | None = None

@app.on_event("startup")
async def startup():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOT, linger_ms=5)
    await producer.start()

@app.on_event("shutdown")
async def shutdown():
    if producer: await producer.stop()

@app.post("/v1/analysis")
async def submit(req: AnalysisRequest):
    job_id = f"anl_{int(time.time()*1000)}"
    msg = {
        "job_id": job_id,
        "video_id": req.video_id,
        "model_version": req.model_version or "mv-0.1.0",
        "artifact_uri": f"s3://bucket/videos/{req.video_id}/source.mp4",
        "requested_by": "usr_system",
        "created_at": nowiso()
    }
    await producer.send_and_wait("analysis.requests", json.dumps(msg).encode("utf-8"), key=req.video_id.encode())
    return {"job_id": job_id, "status": "QUEUED"}
