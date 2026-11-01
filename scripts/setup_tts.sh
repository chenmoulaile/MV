#!/bin/bash
# TTS stack: torch cpu + GPT-SoVITS deps + repo + yt-dlp
exec > /home/z/my-project/scripts/tts_env.log 2>&1
set -x
cd /home/z/my-project/workspace/tts

PY=/home/z/.venv/bin/pip
PY3=/home/z/.venv/bin/python3

# 1. torch cpu
for i in 1 2 3; do $PY install --index-url https://download.pytorch.org/whl/cpu "torch==2.5.1+cpu" && break; sleep 3; done

# 2. other deps (aliyun mirror, fallback pypi)
DEPS="transformers==4.57.1 librosa==0.11.0 soundfile scipy numpy cn2an pypinyin jieba faster-whisper gym grpcio protobuf pyyaml requests tqdm pslocal uvicorn fastapi python-multipart"
for i in 1 2 3; do $PY install -q $DEPS -i https://mirrors.aliyun.com/pypi/simple/ && break
$PY install -q $DEPS && break; sleep 3; done

# 3. GPT-SoVITS repo
for i in 1 2 3; do git clone --depth 1 https://github.com/RVC-Boss/GPT-SoVITS && break; sleep 3; done

# 4. yt-dlp static binary
for i in 1 2 3; do curl -sL -o /home/z/my-project/scripts/yt-dlp "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp" && chmod +x /home/z/my-project/scripts/yt-dlp && break; sleep 3; done

echo "=== TTS ENV DONE $(date)"
$PY3 -c "import torch, transformers, librosa; print('torch', torch.__version__, '| tf', transformers.__version__)"
ls -la /home/z/my-project/scripts/yt-dlp
