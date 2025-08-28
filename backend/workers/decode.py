import subprocess, tempfile, os
from workers.base import Worker

class DecodeWorker(Worker):
    async def handle(self, req):
        await self.emit_progress(req["job_id"], "RECEIVED")
        # TODO: Download object from S3 to tempdir; write preview.gif & metadata.json via ffmpeg/ffprobe
        await self.emit_progress(req['job_id'], 'DECODED', {'preview':'ok'})
        return req

if __name__=='__main__':
    import asyncio
    asyncio.run(DecodeWorker('decode','analysis.requests','pose.requests').start())
