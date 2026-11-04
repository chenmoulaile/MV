#!/usr/bin/env python3
"""Chunked subtitle burn: per-slice ASS + encode + lossless concat."""
import subprocess, os

TMP = '/home/z/my-project/download/_build'
MIX = '/tmp/audiotest.mp4'
OUT = '/home/z/my-project/download/algorithm-competition-assistant-ep1.mp4'

PLAN = [
    ('vo01.wav', 11.2), ('vo02.wav', 5.8), ('vo03.wav', 6.4), ('vo04.wav', 7.5),
    ('vo05.wav', 6.0), ('vo06.wav', 7.5), ('vo07.wav', 5.2), ('vo08.wav', 5.0),
    ('vo09.wav', 7.2), ('vo10.wav', 8.6), ('vo11.wav', 6.0),
]
TEXTS = {
    'vo01': ['平时写算法题，是不是老得在浏览器和编辑器中间来回切？', '题面看一半，样例还得自己手动贴，真的挺烦的。'],
    'vo02': ['今天给大家看一个 Sublime 的插件，专门治这个。'],
    'vo03': ['我随便找了一道题，浏览器里正常打开，网址复制一下。'],
    'vo04': ['回到编辑器，把这个网址丢给它', '题面、样例，它自己全抓进来了。'],
    'vo05': ['代码就贴在下面，该咋写咋写，跟平时一模一样。'],
    'vo06': ['写完按一下运行，几个测试点、用时多少、吃多少内存，直接排在右边。'],
    'vo07': ['全绿，这题就算过了，连答案都不用自己对。'],
    'vo08': ['界面中英文都有，按个人口味随便切。'],
    'vo09': ['另外，对拍、练习统计、比赛计时器这些小工具，它也全给你备好了。'],
    'vo10': ['这个插件已经上架官方的 Package Control 了，装起来就是搜个名字的事。'],
    'vo11': ['这期先混个脸熟，具体怎么玩，下期接着聊。'],
}
NAME_NOTE = {'vo02': 'Algorithm Competition Assistant · 算法竞赛助手',
             'vo10': 'Package Control 搜索 Algorithm Competition Assistant 即可安装'}
TITLE_AT = (1, 5.8, '把刷题搬进 Sublime')  # slice index 1


def at(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f'{h}:{m:02d}:{s:05.2f}'


def vdur(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', p], capture_output=True, text=True)
    return float(r.stdout.strip())


HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Noto Sans SC,46,&H00F4FFEA,&H00FFFFFF,&H00143028,&H8C14243C,0,0,0,0,100,100,0.5,0,3,8,0,2,120,120,64,1
Style: Note,Noto Sans SC,33,&H00FFF0C8,&H00FFFFFF,&H00143028,&H8C14243C,1,0,0,0,100,100,0.5,0,3,6,0,2,120,120,26,1
Style: Title,Noto Sans SC,96,&H00FFFFFF,&H00FFFFFF,&H008C2E1A10,&H96000000,1,0,0,0,100,100,2,0,1,4,2,8,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

parts = []
for i, (vo, dur) in enumerate(PLAN):
    key = vo.replace('.wav', '')
    sf = f'{TMP}/s{i:02d}.mp4'
    events = []
    st, en = 0.35, dur - 0.15
    for t in TEXTS[key]:
        events.append(f'Dialogue: 0,{at(st)},{at(en)},Sub,,0,0,0,,{t}')
    if key in NAME_NOTE:
        events.append(f'Dialogue: 1,{at(st)},{at(en)},Note,,0,0,0,,{NAME_NOTE[key]}')
    if i == TITLE_AT[0]:
        events.append(f'Dialogue: 2,{at(0.3)},{at(TITLE_AT[1]-0.3)},Title,,0,0,0,,{{\\fad(450,450)}}{TITLE_AT[2]}')
    ap = f'{TMP}/sub{i:02d}.ass'
    with open(ap, 'w') as f:
        f.write(HEAD + '\n'.join(events) + '\n')
    outv = f'{TMP}/burn{i:02d}.mp4'
    # burn subtitles + mux mixed-audio slice
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', sf,
                    '-vf', f'ass={ap}:fontsdir=/usr/share/fonts',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                    '-pix_fmt', 'yuv420p', '-an', outv], check=True)
    au = f'{TMP}/au{i:02d}.m4a'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{sum(d for _, d in PLAN[:i]):.3f}',
                    '-t', f'{dur:.3f}', '-i', MIX, '-vn', '-c:a', 'copy', au], check=True)
    fin = f'{TMP}/part{i:02d}.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', outv, '-i', au,
                    '-map', '0:v', '-map', '1:a', '-c', 'copy', '-movflags', '+faststart', fin], check=True)
    parts.append(fin)
    print(f'slice {i} ok {dur}s')

with open(f'{TMP}/list2.txt', 'w') as f:
    for p in parts:
        f.write(f"file '{p}'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
                '-i', f'{TMP}/list2.txt', '-c', 'copy', OUT], check=True)
print('FINAL', OUT, round(vdur(OUT), 2), os.path.getsize(OUT))
