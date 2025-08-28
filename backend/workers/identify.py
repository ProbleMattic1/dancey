from workers.base import Worker
import json

class IdentifyWorker(Worker):
    async def handle(self, req):
        await self.emit_progress(req['job_id'], 'IDENTIFY_STARTED')
        # TODO: score segments with templates/classifier; return ranked alts
        segments=[{'start_ms':1000,'end_ms':2000,'move_id':'mv_arm_wave','confidence':0.82,'alts':[{'move_id':'mv_body_wave','confidence':0.61}]}]
        await self.emit_progress(req['job_id'], 'IDENTIFIED', {'segments': len(segments)})
        await self.producer.send_and_wait('analysis.results', json.dumps({
            'job_id': req['job_id'], 'video_id': req['video_id'], 'model_version': req['model_version'],
            'segments': segments, 'ts': nowiso()
        }).encode())
        return None

if __name__=='__main__':
    import asyncio
    asyncio.run(IdentifyWorker('identify','identify.requests','index.requests').start())
