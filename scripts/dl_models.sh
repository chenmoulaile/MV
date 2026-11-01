#!/bin/bash
# Download GPT-SoVITS pretrained models from hf-mirror with resume
BASE=/home/z/my-project/workspace/tts/gptsovits_pretrained
mkdir -p $BASE/gsv-v2final-pretrained $BASE/chinese-hubert-base $BASE/chinese-roberta-wwm-ext-large
R=https://hf-mirror.com/lj1995/GPT-SoVITS/resolve/main

dl() { # url out
  for i in 1 2 3 4 5 6 7 8; do
    wget -c -q --timeout=30 "$1" -O "$2.part" && mv "$2.part" "$2" && return 0
    sleep 2
  done
  return 1
}

echo "[1/4] hubert $(date)"
dl $R/chinese-hubert-base/pytorch_model.bin $BASE/chinese-hubert-base/pytorch_model.bin
echo "[2/4] gpt v2 $(date)"
dl "$R/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch%3D12-step%3D369668.ckpt" "$BASE/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt"
echo "[3/4] sovits v2 $(date)"
dl $R/gsv-v2final-pretrained/s2G2333k.pth $BASE/gsv-v2final-pretrained/s2G2333k.pth
echo "[4/4] roberta $(date)"
dl $R/chinese-roberta-wwm-ext-large/pytorch_model.bin $BASE/chinese-roberta-wwm-ext-large/pytorch_model.bin
echo "=== ALL DONE $(date)"
ls -la $BASE/*/ | grep -v part
