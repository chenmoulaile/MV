#!/usr/bin/env python3
"""Phase 2: subtitles + audio mix on existing silent.mp4 (veryfast encode)."""
import subprocess, os

F = '/home/z/my-project/download/footage'
VO = '/home/z/my-project/workspace/tts/vo'
OUT = '/home/z/my-project/download'
TMP = f'{OUT}/_build'
FINAL = f'{OUT}/algorithm-competition-assistant-ep1-v2.mp4'

PLAN = [
    ('seg_cold.mkv',   0.0, 11.2, 'vo01.wav'),
    ('seg_outro.mkv',  1.0,  5.8, 'vo02.wav'),
    ('seg_grab.mp4',   0.5,  6.4, 'vo03.wav'),
    ('seg_core.mkv',  10.8,  7.5, 'vo04.wav'),
    ('seg_core.mkv',  33.0,  6.0, 'vo05.wav'),
    ('seg_core.mkv',  40.0,  7.5, 'vo06.wav'),
    ('seg_core.mkv',  55.0,  5.2, 'vo07.wav'),
    ('seg_lang.mkv',   2.0,  5.0, 'vo08.wav'),
    ('seg_tools.mkv',  2.0,  7.2, 'vo09.wav'),
    ('seg_install.mkv',3.0,  8.6, 'vo10.wav'),
    ('seg_outro.mkv',  4.0,  6.0, 'vo11.wav'),
]

def vdur(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', p], capture_output=True, text=True)
    return float(r.stdout.strip())

total = vdur(f'{TMP}/silent.mp4')
fc = []
mix_ins = []
for i, (src, ip, dur, vo) in enumerate(PLAN):
    delay_ms = int((starts_delay(i)) * 1000) if False else 0
# recompute starts from PLAN durations
starts = []
cur = 0.0
for i, (src, ip, dur, vo) in enumerate(PLAN):
    starts.append(cur)
    cur += vdur(f'{TMP}/s{i:02d}.mp4')
total = cur

fc = []
mix_ins = []
for i, (src, ip, dur, vo) in enumerate(PLAN):
    delay_ms = int((starts[i] + 0.35) * 1000)
    fc.append(f'[{i+1}:a]aresample=44100,adelay={delay_ms}|{delay_ms}[a{i}]')
    mix_ins.append(f'[a{i}]')
bgm_idx = len(PLAN) + 1
fc.append(f'[{bgm_idx}:a]atrim=0:{total:.2f},aresample=44100,volume=0.55,afade=t=in:d=1.5,afade=t=out:st={total-2.6:.2f}:d=2.6[bgm]')
mix_ins.append('[bgm]')
fc.append(f'{"".join(mix_ins)}amix=inputs={len(mix_ins)}:duration=longest:normalize=0,volume=1.0,alimiter=limit=0.95[aout]')
cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{TMP}/silent.mp4']
for _, _, _, vo in PLAN:
    cmd += ['-i', f'{VO}/{vo}']
cmd += ['-i', '/home/z/my-project/download/audio/bgm.wav']
cmd += ['-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[aout]',
        '-vf', f'ass={TMP}/subs.ass:fontsdir=/usr/share/fonts',
        '-c:v', 'libx264', '-preset', 'ultrafast', '-threads', '2', '-crf', '20', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', FINAL]
subprocess.run(cmd, check=True)
print('FINAL OK', FINAL, round(vdur(FINAL), 2), os.path.getsize(FINAL))
