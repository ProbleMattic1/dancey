import os, json, logging
from datetime import datetime, timezone
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

def nowiso(): return datetime.now(timezone.utc).isoformat()
log = logging.getLogger("worker"); logging.basicConfig(level=logging.INFO)

class Worker:
    def __init__(self, name, in_topic, out_topic=None, bootstrap=None):
        self.name=name; self.in_topic=in_topic; self.out_topic=out_topic
        self.bootstrap = bootstrap or os.getenv("KAFKA_BOOT","localhost:9092")
        self.consumer=None; self.producer=None

    async def start(self):
        self.consumer = AIOKafkaConsumer(self.in_topic, bootstrap_servers=self.bootstrap, auto_offset_reset="earliest")
        await self.consumer.start()
        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap)
        await self.producer.start()
        log.info(f"{self.name} started")
        try:
            async for msg in self.consumer:
                payload = json.loads(msg.value)
                try:
                    result = await self.handle(payload)
                    if self.out_topic and result is not None:
                        await self.producer.send_and_wait(self.out_topic, json.dumps(result).encode(), key=msg.key)
                except Exception as e:
                    await self.emit_failure(payload, str(e))
        finally:
            await self.consumer.stop(); await self.producer.stop()

    async def emit_progress(self, job_id, state, metrics=None):
        p = {"job_id": job_id, "state": state, "metrics": metrics or {}, "ts": nowiso()}
        await self.producer.send_and_wait("analysis.progress", json.dumps(p).encode())

    async def emit_failure(self, req, reason):
        p = {"job_id": req.get("job_id"), "video_id": req.get("video_id"), "state":"FAILED","reason": reason, "ts": nowiso()}
        await self.producer.send_and_wait("analysis.failures", json.dumps(p).encode())

    async def handle(self, payload): raise NotImplementedError
