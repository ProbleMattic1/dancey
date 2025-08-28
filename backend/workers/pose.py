from workers.base import Worker

class PoseWorker(Worker):
    async def handle(self, req):
        await self.emit_progress(req['job_id'], 'POSE_STARTED')
        # TODO: run pose estimation and save keypoints.npz to S3
        await self.emit_progress(req['job_id'], 'POSE_DONE', {'frames': 1200, 'fps': 20.0})
        return req

if __name__=='__main__':
    import asyncio
    asyncio.run(PoseWorker('pose','pose.requests','features.requests').start())
