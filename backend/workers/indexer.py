from workers.base import Worker

class IndexWorker(Worker):
    async def handle(self, req):
        await self.emit_progress(req['job_id'], 'INDEX_STARTED')
        # TODO: write segments to DB / search index
        await self.emit_progress(req['job_id'], 'INDEXED')
        return req

if __name__=='__main__':
    import asyncio
    asyncio.run(IndexWorker('index','index.requests',None).start())
