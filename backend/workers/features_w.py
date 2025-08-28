from workers.base import Worker
from ml.features import make_features
import numpy as np

class FeaturesWorker(Worker):
    async def handle(self, req):
        await self.emit_progress(req['job_id'], 'FEATURES_STARTED')
        # TODO: load keypoints from S3, compute features via ml.features.make_features, store features.npz
        await self.emit_progress(req['job_id'], 'FEATURES_DONE', {'feat_dim': 128})
        return req

if __name__=='__main__':
    import asyncio
    asyncio.run(FeaturesWorker('features','features.requests','segment.requests').start())
