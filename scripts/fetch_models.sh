#!/usr/bin/env bash
set -euo pipefail
mkdir -p backend/models
MODEL_URL="${MODEL_URL:-https://example.com/movenet_singlepose_lightning_4.onnx}"
OUT="backend/models/movenet_singlepose_lightning_4.onnx"
echo "Downloading MoveNet ONNX from: $MODEL_URL"
curl -L "$MODEL_URL" -o "$OUT"
echo "Saved to $OUT"
