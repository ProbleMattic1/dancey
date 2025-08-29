import os, requests, sys

API_BASE = os.getenv("API_BASE", "http://danceapp-backend:8000")
VIDEO_ID = os.getenv("VIDEO_ID")

if not VIDEO_ID:
    print("VIDEO_ID env is required", file=sys.stderr)
    sys.exit(2)

r = requests.post(f"{API_BASE}/v1/analysis", json={"video_id": VIDEO_ID})
r.raise_for_status()
print("Queued job:", r.json())
