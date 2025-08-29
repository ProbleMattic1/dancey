import os, io, tempfile, json, math
import numpy as np
from workers.base import Worker
from app.common.s3util import s3_client, parse_s3_uri

MODEL_PATH = os.getenv("POSE_ONNX_PATH", "backend/models/movenet_singlepose_lightning_4.onnx")
TFLITE_MODEL_PATH = os.getenv("POSE_TFLITE_PATH", "backend/models/movenet_singlepose_lightning_4.tflite")

def infer_movenet(session, frame_rgb):
    import cv2
    H, W, _ = frame_rgb.shape
    inp = cv2.resize(frame_rgb, (192,192)).astype("float32")/255.0
    inp = np.expand_dims(inp, axis=0)  # [1,192,192,3]
    input_name = session.get_inputs()[0].name
    out = session.run(None, {input_name: inp})
    kps = out[0].reshape(1,17,3)[0]  # y, x, score
    xy = np.stack([kps[:,1]*W, kps[:,0]*H], axis=-1) / np.array([[W,H]], dtype="float32")
    conf = kps[:,2].astype("float32")
    return xy, conf

def sample_frames_ffmpeg(src_path, fps=20):
    import cv2
    cap = cv2.VideoCapture(src_path)
    native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, int(round(native_fps / fps)))
    frames = []; i=0
    while True:
        ok, frame_bgr = cap.read()
        if not ok: break
        if i % step == 0:
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)
        i += 1
    cap.release()
    return frames, native_fps

class PoseWorker(Worker):
    async def handle(self, req):
        await self.emit_progress(req['job_id'], 'POSE_STARTED')
        s3 = s3_client()
        bucket, key = parse_s3_uri(req["artifact_uri"])
        with tempfile.TemporaryDirectory() as td:
            src = os.path.join(td, "src.mp4")
            try:
                s3.download_file(bucket, key, src)
            except Exception as e:
                await self.emit_failure(req, f"download failed: {e}")
                return None

            frames, native_fps = sample_frames_ffmpeg(src, fps=20)
            T = len(frames)
            J = 17
            xy = np.zeros((T,J,2), dtype="float32")
            conf = np.zeros((T,J), dtype="float32")

            session = None
            tflite = None
            if os.path.exists(MODEL_PATH):
                try:
                    import onnxruntime as ort
                    session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
                except Exception:
                    session = None
            if session is None and os.path.exists(TFLITE_MODEL_PATH):
                try:
                    try:
                        from tflite_runtime.interpreter import Interpreter
                    except Exception:
                        from tensorflow.lite import Interpreter  # type: ignore
                    tflite = Interpreter(model_path=TFLITE_MODEL_PATH)
                    tflite.allocate_tensors()
                except Exception:
                    tflite = None
                try:
                    import onnxruntime as ort
                    session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])
                except Exception:
                    session = None
            tflite = None

            if session:
                for t, frame in enumerate(frames):
                    k_xy, k_conf = infer_movenet(session, frame)
                    if k_xy.shape[0] == J:
                        xy[t] = k_xy; conf[t] = k_conf
                    else:
                        xy[t] = 0.5; conf[t] = 0.1
            elif tflite:
                import numpy as np, cv2
                input_details = tflite.get_input_details(); output_details = tflite.get_output_details()
                for t, frame in enumerate(frames):
                    inp = cv2.resize(frame, (192,192)).astype('float32')/255.0
                    inp = np.expand_dims(inp, 0)
                    tflite.set_tensor(input_details[0]['index'], inp)
                    tflite.invoke()
                    out = tflite.get_tensor(output_details[0]['index']).reshape(1,17,3)[0]
                    xy[t] = np.stack([out[:,1], out[:,0]], -1)  # normalized
                    conf[t] = out[:,2]

                    k_xy, k_conf = infer_movenet(session, frame)
                    if k_xy.shape[0] == J:
                        xy[t] = k_xy; conf[t] = k_conf
                    else:
                        xy[t] = 0.5; conf[t] = 0.1
            else:
                xy[:] = 0.5; conf[:] = 0.1

            bio = io.BytesIO()
            np.savez(bio, xy=xy, conf=conf); bio.seek(0)
            kp_key = f"videos/{req['video_id']}/pose/keypoints_v0.1.npz"
            s3.put_object(Bucket=bucket, Key=kp_key, Body=bio.getvalue(), ContentType="application/octet-stream")
            await self.emit_progress(req['job_id'], 'POSE_DONE', {'frames': int(T), 'fps': float(native_fps)})
        return req

if __name__=='__main__':
    import asyncio
    asyncio.run(PoseWorker('pose','pose.requests','features.requests').start())
