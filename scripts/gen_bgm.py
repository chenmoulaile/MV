#!/usr/bin/env python3
"""合成 BGM（暗色电影氛围垫乐）与音效（whoosh/click/chime）。纯 numpy，无版权问题。"""
import numpy as np
import wave
import os

SR = 48000
DIR = '/home/z/my-project/download/audio'
os.makedirs(DIR, exist_ok=True)


def save(name, data, sr=SR):
    data = np.clip(data, -1, 1)
    pcm = (data * 32767).astype(np.int16)
    if pcm.ndim == 1:
        pcm = np.stack([pcm, pcm], axis=1)
    with wave.open(os.path.join(DIR, name + '.wav'), 'w') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    print(name, '%.1fs' % (pcm.shape[0] / sr))


def env_ad(n, a, d, sr=SR):
    """attack-decay 包络"""
    t = np.arange(n) / sr
    e = np.minimum(t / max(a, 1e-4), 1.0)
    e *= np.exp(-np.maximum(t - a, 0) / d)
    return e


# ---------------------------------------------------------------- BGM ---
DUR = 170.0
n = int(DUR * SR)
t = np.arange(n) / SR
rng = np.random.default_rng(42)

# 1. 低频 drone（A1+A2 失谐叠加，慢呼吸）
breath = 0.6 + 0.25 * np.sin(2 * np.pi * t / 23.0) + 0.15 * np.sin(2 * np.pi * t / 7.7)
drone = (np.sin(2 * np.pi * 55.0 * t) * 0.55
         + np.sin(2 * np.pi * 55.35 * t) * 0.30
         + np.sin(2 * np.pi * 110.2 * t) * 0.22
         + np.sin(2 * np.pi * 164.8 * t) * 0.10)   # E3 五度，一点点色彩
drone *= breath * 0.30

# 2. 心跳脉冲（每 2.4s，48Hz 扫频）
pulse = np.zeros(n)
step = int(2.4 * SR)
pl = int(0.30 * SR)
tp = np.arange(pl) / SR
one = np.sin(2 * np.pi * (52.0 - 40.0 * tp / 0.30) * tp) * env_ad(pl, 0.005, 0.09)
for s in range(0, n - pl, step):
    pulse[s:s + pl] += one * 0.5
    if s + step // 2 + pl < n:      # 半拍后的弱心跳
        pulse[s + step // 2: s + step // 2 + pl] += one * 0.22

# 3. shimmer（稀疏高频音符，五声音阶）
shimmer = np.zeros(n)
notes = [880.0, 987.8, 1174.7, 1318.5, 1568.0]      # A5 B5 D6 E6 G6
pos = 3.0
while pos < DUR - 6:
    f = notes[int(rng.integers(0, len(notes)))]
    ln = int((0.5 + rng.random() * 0.8) * SR)
    if pos * SR + ln >= n:
        break
    tt = np.arange(ln) / SR
    tone = (np.sin(2 * np.pi * f * tt) * 0.5
            + np.sin(2 * np.pi * f * 2.0 * tt) * 0.12) * env_ad(ln, 0.02, 0.5)
    shimmer[int(pos * SR): int(pos * SR) + ln] += tone * 0.06
    pos += 3.0 + rng.random() * 6.0

# 4. 轻噪声床（立体声去相关，营造空气感）
noise = rng.standard_normal(n) * 0.012
noise_l = np.convolve(noise, np.ones(24) / 24, 'same')
noise_r = np.convolve(np.roll(noise, 97), np.ones(24) / 24, 'same')

mix_l = drone + pulse + shimmer + noise_l
mix_r = drone + np.roll(pulse, 13) * 0.96 + np.roll(shimmer, 41) * 0.9 + noise_r

# 立体声 + 首尾淡化
fade_in = int(2.5 * SR)
fade_out = int(5.0 * SR)
mix_l[:fade_in] *= np.linspace(0, 1, fade_in)
mix_r[:fade_in] *= np.linspace(0, 1, fade_in)
mix_l[-fade_out:] *= np.linspace(1, 0, fade_out)
mix_r[-fade_out:] *= np.linspace(1, 0, fade_out)

bgm = np.stack([mix_l, mix_r], axis=1) * 0.85
save('bgm', bgm)

# ---------------------------------------------------------------- SFX ---
# whoosh 0.7s（带通噪声 + 扫频包络）
n_w = int(0.75 * SR)
tw = np.arange(n_w) / SR
noise_w = rng.standard_normal(n_w)
# 简易带通：差分近似
sweep = np.sin(2 * np.pi * (300 + 2200 * tw / 0.75) * tw) * 0.35
body = noise_w * 0.5 + sweep
env_w = np.sin(np.pi * tw / 0.75) ** 2.2
whoosh = body * env_w
save('whoosh', whoosh * 0.8)

# click 40ms
n_c = int(0.05 * SR)
tc = np.arange(n_c) / SR
click = np.sin(2 * np.pi * 1500 * tc) * np.exp(-tc / 0.008) * 0.5
click[:int(0.002 * SR)] += 0.5
save('click', click)

# AC chime（E5→B5 双音）
n_ch = int(1.3 * SR)
tch = np.arange(n_ch) / SR
chime = (np.sin(2 * np.pi * 659.3 * tch) * np.exp(-tch / 0.35) * 0.45
         + np.sin(2 * np.pi * 987.8 * (tch - 0.12).clip(0)) * np.exp(-(tch - 0.12).clip(0) / 0.4) * 0.35 * (tch > 0.12))
save('chime', chime * 0.9)

# riser 1.2s（转场上升）
n_r = int(1.2 * SR)
tr = np.arange(n_r) / SR
riser = np.sin(2 * np.pi * (180 + 900 * (tr / 1.2) ** 2) * tr) * (tr / 1.2) ** 2 * 0.4
riser += rng.standard_normal(n_r) * (tr / 1.2) ** 2 * 0.15
save('riser', riser)

print('ALL_DONE')
