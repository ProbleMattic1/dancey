import os, subprocess, json, time, requests, httpx, tempfile, pathlib

BASE = os.getenv("E2E_BASE","http://localhost:8000")
MINIO_HEALTH = os.getenv("E2E_MINIO","http://localhost:9000/minio/health/ready")

def _wait_url(url, timeout=60):
    start=time.time()
    while time.time()-start<timeout:
        try:
            r=requests.get(url, timeout=2)
            if r.status_code in (200,204,403): return True
        except Exception:
            pass
        time.sleep(2)
    return False

def _make_test_mp4(path):
    # Create a 2s 360p color video using ffmpeg
    cmd = ["ffmpeg","-y","-f","lavfi","-i","color=c=blue:s=360x640:d=2","-r","25", path]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def test_end_to_end(skip_if_down=True):
    if os.getenv("E2E","false").lower()!="true":
        import pytest; pytest.skip("E2E disabled (set E2E=true)")

    assert _wait_url(BASE+"/health"), "backend not reachable"
    assert _wait_url(MINIO_HEALTH), "minio not ready"

    mp4 = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
    _make_test_mp4(mp4)

    # 1) sign upload
    r = requests.post(f"{BASE}/v1/uploads/sign", json={"filename":"e2e.mp4","content_type":"video/mp4"}); r.raise_for_status()
    sign = r.json()

    # 2) PUT to presigned URL
    with open(mp4, "rb") as fh:
        put = requests.put(sign["url"], data=fh, headers={"Content-Type":"video/mp4"})
        assert 200 <= put.status_code < 400

    # 3) create video
    r = requests.post(f"{BASE}/v1/videos", json={"upload_id":sign["upload_id"], "key":sign["key"]}); r.raise_for_status()
    vid = r.json()["video_id"]

    # 4) analyze
    r = requests.post(f"{BASE}/v1/analysis", json={"video_id": vid}); r.raise_for_status()
    job = r.json()

    # 5) poll for preview/segments (decode step updates DB; identify/index are stubs but should succeed)
    ok=False
    for _ in range(30):
        time.sleep(2)
        v = requests.get(f"{BASE}/v1/videos/{vid}").json()
        if v.get("preview_url"): ok=True; break
    assert ok, "preview not generated"

    segs = requests.get(f"{BASE}/v1/videos/{vid}/segments").json().get("segments", [])
    assert isinstance(segs, list)
