#!/usr/bin/env python3
"""Assemble the promo video: segments → concat → subtitles → VO+BGM mix.
Timeline (seconds):
S1 teaser   0.0-8.0      l01@0.7  l02@4.6
S2 title    8.0-11.2
S3 install  11.2-27.1    l03@12.0
S4 grab     27.1-39.2    l04@27.8 l05@34.0
S5 paste    39.2-47.7    l06@39.9
S6 run      47.7-60.2    l07@48.4 l08@52.5
S7 detail   60.2-68.7    l09@60.9
S8 lang     68.7-78.7    l10@69.4
S9 outro1   78.7-87.7    l11@79.3
S10 outro2  87.7-94.9    l12@88.3  (fade out 92.5-94.9)
"""
import os, subprocess, json

T = "/home/z/my-project/workspace/takes2"
C = "/home/z/my-project/workspace/cards"
V = "/home/z/my-project/workspace/vo_out"
A = "/home/z/my-project/workspace/assets"
W = "/home/z/my-project/workspace/assembly"
os.makedirs(W, exist_ok=True)
os.chdir(W)

FPS = 30
VSCALE = "scale=1920:1080:flags=lanczos,fps=30,format=yuv420p"

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", cmd[:180], "\n", r.stderr[-600:])
        raise SystemExit(1)

# ---- 1) per-segment normalized silent intermediates ----
print("seg S1 teaser")
run(f"ffmpeg -y -v error -ss 0.2 -to 8.2 -i {T}/seg_teaser.mp4 -vf \"{VSCALE}\" -an -c:v libx264 -preset veryfast -crf 19 s1.mp4")
print("seg S3 install 1.6x")
run(f"ffmpeg -y -v error -ss 1.2 -to 26.7 -i {T}/seg_install.mp4 -vf \"setpts=PTS/1.6,{VSCALE}\" -an -c:v libx264 -preset veryfast -crf 19 s3.mp4")
print("seg S4 grab + masks")
run(f"ffmpeg -y -v error -i {T}/seg_grab.mp4 -vf \"drawbox=x=0:y=104:w=1920:h=48:color=white:t=fill,drawbox=x=985:y=945:w=935:h=135:color=0xF7F8FB:t=fill,{VSCALE}\" -an -c:v libx264 -preset veryfast -crf 19 s4.mp4")
print("seg S5 paste")
run(f"ffmpeg -y -v error -ss 1.0 -to 9.5 -i {T}/seg_run.mp4 -vf \"{VSCALE}\" -an -c:v libx264 -preset veryfast -crf 19 s5.mp4")
print("seg S6 run cards")
run(f"ffmpeg -y -v error -ss 9.5 -to 22.0 -i {T}/seg_run.mp4 -vf \"{VSCALE}\" -an -c:v libx264 -preset veryfast -crf 19 s6.mp4")
print("seg S7 detail")
run(f"ffmpeg -y -v error -i {T}/seg_detail.mp4 -vf \"{VSCALE}\" -an -c:v libx264 -preset veryfast -crf 19 s7.mp4")
print("seg S8 lang")
run(f"ffmpeg -y -v error -ss 1.0 -to 11.0 -i {T}/seg_lang.mp4 -vf \"{VSCALE}\" -an -c:v libx264 -preset veryfast -crf 19 s8.mp4")

def card(png, dur, out, fade_in=0.4, fade_out=0.4):
    run(f"ffmpeg -y -v error -loop 1 -t {dur} -i {png} -vf \"scale=1920:1080,fps=30,format=yuv420p,fade=t=in:st=0:d={fade_in},fade=t=out:st={dur-fade_out}:d={fade_out}\" -an -c:v libx264 -preset veryfast -crf 19 {out}")

print("cards")
card(f"{C}/card_title.png", 3.2, "s2.mp4")
card(f"{C}/card_outro1.png", 9.0, "s9.mp4", 0.4, 0.3)
card(f"{C}/card_outro2.png", 7.2, "s10.mp4", 0.4, 1.6)

# ---- 2) concat video ----
print("concat")
with open("concat.txt", "w") as f:
    for s in ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10"]:
        f.write(f"file '{W}/{s}.mp4'\n")
run("ffmpeg -y -v error -f concat -safe 0 -i concat.txt -c copy video_noaudio.mp4")

# ---- 3) subtitles (ASS) ----
# durations of VO lines
dur = {}
for i in range(1, 13):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", f"{V}/l{i:02d}.wav"], capture_output=True, text=True)
    dur[i] = float(r.stdout.strip())

VO_START = {1: 0.7, 2: 4.6, 3: 12.0, 4: 27.8, 5: 34.0, 6: 39.9, 7: 48.4, 8: 52.5, 9: 60.9, 10: 69.4, 11: 79.3, 12: 88.3}

SUBS = {
    1:  ("每一个打比赛的人，都有自己的一套调试习惯", []),
    2:  ("我的那套，现在整个搬进了 Sublime Text", []),
    3:  ("开始之前，先把它装上。Package Control 里搜 {Algorithm Competition Assistant}，回车", ["Algorithm Competition Assistant"]),
    4:  ("比赛的时候，最烦的就是抄样例。打开题目页，在浏览器里点一下扩展", []),
    5:  ("回到编辑器，一个快捷键，题面和样例，就都摆在这了", []),
    6:  ("代码贴在最下面。等它编译的时候，我们来聊聊它是什么", []),
    7:  ("一个快捷键，编译、运行、判题，一次完成", []),
    8:  ("每个测试点的用时和内存，都是从真实进程量出来的，不是估的", []),
    9:  ("每个测试点都能点开详情，输入、期望、实际，一屏看全", []),
    10: ("界面中英文都齐了，随手就能切换", []),
    11: ("它基于 {FastOlympicCoding} 开发，判题显示参考了 {cph-ng}，浏览器抓题的思路来自 {FastOlympicCodingHook}",
         ["FastOlympicCoding", "cph-ng", "FastOlympicCodingHook"]),
    12: ("本地测评，就在手边。官方 {Package Control}，已经收录", ["Package Control"]),
}

def ass_time(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def esc(t):
    return t.replace("{", "\u300a").replace("}", "\u300b")

lines = []
for i, (txt, names) in SUBS.items():
    st = VO_START[i]; en = st + dur[i] + 0.25
    body = esc(txt)
    for n in names:
        body = body.replace(n, "{\\c&H58DC96&}" + n + "{\\c&HFFFFFF&}")
    lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},Sub,,0,0,0,,{body}")

ass_header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Noto Sans SC,58,&H00FFFFFF,&H00FFFFFF,&H00101018,&H96000000,0,0,0,0,100,100,0,0,1,3,1,2,60,60,64,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open("subs.ass", "w") as f:
    f.write(ass_header + "\n".join(lines) + "\n")
print("subs written:", len(lines), "lines")

# ---- 4) VO track ----
print("vo track")
parts = []
t = 0
inputs = []
filters = []
idx = 0
for i in range(1, 13):
    st = VO_START[i]
    inputs.append(f"-i {V}/l{i:02d}.wav")
    # loudnorm-ish: volume boost then place; F5 output is quiet-ish
    filters.append(f"[{idx}:a]aresample=44100,volume=1.9,adelay={int(st*1000)}|{int(st*1000)}[a{idx}]")
    idx += 1
total = 95.5
mix = "".join(f"[a{k}]" for k in range(idx))
fc = " ".join(filters) + f";{mix}amix=inputs={idx}:normalize=0,apad=whole_dur={total}[vo]"
run("ffmpeg -y -v error " + " ".join(inputs) + ' -filter_complex "' + fc + '" -map "[vo]" -ar 44100 -ac 2 vo_track.wav')

# ---- 5) BGM ----
print("bgm")
run(f"ffmpeg -y -v error -i {A}/bgm.wav -af \"atrim=0:{total},volume=0.24,afade=t=in:st=0:d=1.5,afade=t=out:st={total-3}:d=3,aresample=44100\" -ar 44100 -ac 2 bgm_track.wav")

# ---- 6) final mix + subtitles ----
print("final")
run('ffmpeg -y -v error -i video_noaudio.mp4 -i vo_track.wav -i bgm_track.wav '
    '-filter_complex "[0:v]ass=subs.ass[v];[1:a][2:a]amix=inputs=2:duration=first:normalize=0,volume=1.0[a]" '
    '-map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 19 -c:a aac -b:a 192k -shortest final_mv.mp4')
print("FINAL DONE")
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", "final_mv.mp4"],
                   capture_output=True, text=True)
print(r.stdout)
