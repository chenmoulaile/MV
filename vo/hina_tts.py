#!/usr/bin/env python3
"""Hina (Sorasaki Hina) voice clone synthesis via F5-TTS v1 on CPU.
Usage: python3 hina_tts.py <lines.jsonl> <outdir>
lines.jsonl: {"id": "...", "text": "..."} per line.
"""
import json, os, sys, time, resource

BASE = "/home/z/my-project/workspace"
REF = f"{BASE}/assets/ref_w1_24k.wav"
REF_TEXT = "老师，想做什么我都会尽力帮忙的。需要的时候，和我说就好。"
MODEL_DIR = f"{BASE}/models/F5TTS_v1_Base"
VOCOS_DIR = f"{BASE}/models/vocos-mel-24khz"
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else f"{BASE}/vo_out"
os.makedirs(OUTDIR, exist_ok=True)

import torch, torchaudio
print("torch", torch.__version__, "threads", torch.get_num_threads(), flush=True)
torch.set_num_threads(2)

from f5_tts.infer.utils_infer import load_vocoder, load_model, preprocess_ref_audio_text, infer_process
from f5_tts.model import DiT
import yaml

with open("/home/z/.venv/lib/python3.12/site-packages/f5_tts/configs/F5TTS_v1_Base.yaml") as f:
    ycfg = yaml.safe_load(f)
arch = ycfg["model"]["arch"]
model_cfg = dict(arch)  # passed straight to DiT(**cfg)
if "attn_backend" in model_cfg: model_cfg.pop("attn_backend")
if "text_mask_padding" in model_cfg: model_cfg.pop("text_mask_padding")
if "checkpoint_activations" in model_cfg: model_cfg.pop("checkpoint_activations")
vocab = open(f"{MODEL_DIR}/vocab.txt", "r", encoding="utf-8").readlines()

print("loading vocoder...", flush=True)
t0 = time.time()
vocoder = load_vocoder(is_local=True, local_path=VOCOS_DIR)
print(f"vocoder loaded {time.time()-t0:.1f}s", flush=True)

print("loading model...", flush=True)
t0 = time.time()
model = load_model(DiT, model_cfg, f"{MODEL_DIR}/model_1250000.safetensors")
print(f"model loaded {time.time()-t0:.1f}s rss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024}MB", flush=True)

ref_audio, ref_text = preprocess_ref_audio_text(REF, REF_TEXT)
print("ref ready:", ref_text, flush=True)

lines = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
for it in lines:
    lid, text = it["id"], it["text"]
    out = f"{OUTDIR}/{lid}.wav"
    if os.path.exists(out) and os.path.getsize(out) > 40000:
        print("skip", lid, flush=True); continue
    t0 = time.time()
    wav, sr, _spec = infer_process(ref_audio, ref_text, text, model, vocoder,
                            speed=it.get("speed", 1.0), cross_fade_duration=0.15,
                            nfe_step=16)
    torchaudio.save(out, torch.tensor(wav).unsqueeze(0), sr)
    print(f"DONE {lid} {time.time()-t0:.1f}s -> {out}", flush=True)

print("ALL_LINES_DONE", flush=True)
