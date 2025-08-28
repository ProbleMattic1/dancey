from workers.base import Worker
import json

class SegmentWorker(Worker):
    async def handle(self, req):
        await self.emit_progress(req['job_id'], 'SEGMENT_STARTED')
        # TODO: heuristic change-point detection, produce candidate windows
        candidates=[{'start_ms':1000,'end_ms':2000}]
        req['candidates']=candidates
        await self.emit_progress(req['job_id'], 'SEGMENTED', {'cand': len(candidates)})
        return req

if __name__=='__main__':
    import asyncio
    asyncio.run(SegmentWorker('segment','segment.requests','identify.requests').start())
