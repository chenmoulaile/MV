#!/bin/bash
# Download GPT-SoVITS pretrained models via curl with resume
BASE=/home/z/my-project/workspace/tts/gptsovits_pretrained
mkdir -p $BASE/gsv-v2final-pretrained $BASE/chinese-hubert-base $BASE/chinese-roberta-wwm-ext-large
R=https://hf-mirror.com/lj1995/GPT-SoVITS/resolve/main

dl() {
  for i in 1 2 3 4 5 6 7 8 9 10; do
    curl -sL -C - --max-time 600 --retry 2 "$1" -o "$2" && return 0
    sleep 2
  done
  return 1
}

echo "[1/4] sovits v2 $(date +%H:%M:%S)"
dl "$R/gsv-v2final-pretrained/s2G2333k.pth" "$BASE/gsv-v2final-pretrained/s2G2333k.pth"
echo "[2/4] gpt v2 $(date +%H:%M:%S)"
dl "$R/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt" "$BASE/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt"
echo "[3/4] hubert $(date +%H:%M:%S)"
dl "$R/chinese-hubert-base/pytorch_model.bin" "$BASE/chinese-hubert-base/pytorch_model.bin"
echo "[4/4] roberta $(date +%H:%M:%S)"
dl "$R/chinese-roberta-wwm-ext-large/pytorch_model.bin" "$BASE/chinese-roberta-wwm-ext-large/pytorch_model.bin"
echo "=== ALL DONE $(date +%H:%M:%S)"
ls -la $BASE/gsv-v2final-pretrained/ $BASE/chinese-hubert-base/ $BASE/chinese-roberta-wwm-ext-large/
