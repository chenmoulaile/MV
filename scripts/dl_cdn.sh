#!/bin/bash
# Models via ModelScope CDN with parallel ranges
exec > /home/z/my-project/scripts/dl_cdn.log 2>&1
set -x
BASE=/home/z/my-project/workspace/tts/gptsovits_pretrained
R="https://modelscope.cn/api/v1/models/AI-ModelScope/GPT-SoVITS/repo?FilePath="

rm -f $BASE/gsv-v2final-pretrained/*.pth $BASE/gsv-v2final-pretrained/*.ckpt $BASE/chinese-hubert-base/*.bin $BASE/chinese-roberta-wwm-ext-large/*.bin

redir() { curl -sI --max-time 30 "${R}$1&Revision=master" | grep -i "^location:" | tr -d '\r' | cut -d' ' -f2; }

for spec in \
  "gsv-v2final-pretrained/s2G2333k.pth|$BASE/gsv-v2final-pretrained/s2G2333k.pth" \
  "gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch%3D12-step%3D369668.ckpt|$BASE/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt" \
  "chinese-hubert-base/pytorch_model.bin|$BASE/chinese-hubert-base/pytorch_model.bin" \
  "chinese-roberta-wwm-ext-large/pytorch_model.bin|$BASE/chinese-roberta-wwm-ext-large/pytorch_model.bin" ; do
  fp="${spec%%|*}"; out="${spec##*|}"
  url=$(redir "$fp")
  echo "URL: $url"
  python3 /home/z/my-project/scripts/pdl.py "$url" "$out" 16
done
echo "=== CDN MODELS DONE $(date +%H:%M:%S)"
ls -la $BASE/gsv-v2final-pretrained/ $BASE/chinese-hubert-base/ $BASE/chinese-roberta-wwm-ext-large/
# torch + deps continue
curl -sL --retry 3 -o /tmp/torch_cpu.whl "https://mirrors.aliyun.com/pytorch-wheels/cpu/torch-2.5.1%2Bcpu-cp312-cp312-linux_x86_64.whl" && /home/z/.venv/bin/pip install -q /tmp/torch_cpu.whl && echo "TORCH INSTALLED"
/home/z/.venv/bin/pip install -q transformers==4.57.1 librosa soundfile scipy "numpy<2" cn2an pypinyin jieba requests tqdm -i https://mirrors.aliyun.com/pypi/simple/ && echo "DEPS INSTALLED"
/home/z/.venv/bin/pip install -q yt-dlp -i https://mirrors.aliyun.com/pypi/simple/ && echo "YTDLP OK"
/home/z/.venv/bin/python3 -c "import torch, transformers, librosa; print('STACK OK', torch.__version__)"
echo "=== ALL DONE $(date +%H:%M:%S)"
