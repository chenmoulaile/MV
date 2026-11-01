#!/bin/bash
# All downloads via fast CN mirrors
exec > /home/z/my-project/scripts/dl_cn.log 2>&1
set -x
BASE=/home/z/my-project/workspace/tts/gptsovits_pretrained
PY3=/home/z/.venv/bin/python3

msdl() { # filepath out
  curl -sL --retry 3 --max-time 900 "https://modelscope.cn/api/v1/models/AI-ModelScope/GPT-SoVITS/repo?FilePath=$1&Revision=master" -o "$2"
}

mkdir -p $BASE/gsv-v2final-pretrained $BASE/chinese-hubert-base $BASE/chinese-roberta-wwm-ext-large

msdl "chinese-hubert-base/pytorch_model.bin" "$BASE/chinese-hubert-base/pytorch_model.bin" &
P1=$!
msdl "gsv-v2final-pretrained/s2G2333k.pth" "$BASE/gsv-v2final-pretrained/s2G2333k.pth" &
P2=$!
msdl "gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch%3D12-step%3D369668.ckpt" "$BASE/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt" &
P3=$!
msdl "chinese-roberta-wwm-ext-large/pytorch_model.bin" "$BASE/chinese-roberta-wwm-ext-large/pytorch_model.bin" &
P4=$!

wait $P1 $P2 $P3 $P4
echo "=== MODELS DONE $(date +%H:%M:%S)"
ls -la $BASE/gsv-v2final-pretrained/ $BASE/chinese-hubert-base/ $BASE/chinese-roberta-wwm-ext-large/

# torch cpu from aliyun pytorch-wheels mirror
curl -sL --retry 3 -o /tmp/torch_cpu.whl "https://mirrors.aliyun.com/pytorch-wheels/cpu/torch-2.5.1%2Bcpu-cp312-cp312-linux_x86_64.whl" && \
/home/z/.venv/bin/pip install -q /tmp/torch_cpu.whl && echo "TORCH INSTALLED"

# other deps via aliyun
/home/z/.venv/bin/pip install -q transformers==4.57.1 librosa soundfile scipy "numpy<2" cn2an pypinyin jieba requests tqdm -i https://mirrors.aliyun.com/pypi/simple/ && echo "DEPS INSTALLED"

# yt-dlp via aliyun pip
/home/z/.venv/bin/pip install -q yt-dlp -i https://mirrors.aliyun.com/pypi/simple/ && /home/z/.venv/bin/yt-dlp --version && echo "YTDLP OK"

$PY3 -c "import torch, transformers, librosa; print('STACK OK', torch.__version__)"
echo "=== ALL DONE $(date +%H:%M:%S)"
