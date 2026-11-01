#!/usr/bin/env python3
"""Final assembly: slices -> concat -> subtitles(ASS) -> VO mix + BGM."""
import subprocess, os, json

F = '/home/z/my-project/download/footage'
VO = '/home/z/my-project/workspace/tts/vo'
OUT = '/home/z/my-project/download'
TMP = f'{OUT}/_build'
os.makedirs(TMP, exist_ok=True)
FINAL = f'{OUT}/algorithm-competition-assistant-ep1.mp4'
FPS = 30

# (source, in_point, duration, vo_file)
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
NAME_NOTE = {
    'vo02': 'Algorithm Competition Assistant · 算法竞赛助手',
    'vo10': 'Package Control 搜索 Algorithm Competition Assistant 即可安装',
}
TITLE_AT = (11.2, 5.8, '把刷题搬进 Sublime')  # seg2 start, dur, text


def vdur(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', p], capture_output=True, text=True)
    return float(r.stdout.strip())


def ass_time(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f'{h:d}:{m:02d}:{s:05.2f}'


# 1. slices
seg_files = []
starts = []
cur = 0.0
for i, (src, ip, dur, vo) in enumerate(PLAN):
    sf = f'{TMP}/s{i:02d}.mp4'
    src_full = f'{F}/{src}' if not src.startswith('/') else src
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(ip), '-i', src_full,
                    '-t', str(dur), '-r', str(FPS), '-vf',
                    'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p',
                    '-an', sf], check=True)
    seg_files.append(sf)
    starts.append(cur)
    cur += vdur(sf)
total = cur
print('segments ok, total', round(total, 2))

# 2. concat
with open(f'{TMP}/list.txt', 'w') as f:
    for sf in seg_files:
        f.write(f"file '{sf}'\n")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
                '-i', f'{TMP}/list.txt', '-c', 'copy', f'{TMP}/silent.mp4'], check=True)
print('concat ok', round(vdur(f'{TMP}/silent.mp4'), 2))

# 3. subtitles
lines = []
lines.append('[Script Info]')
lines.append('ScriptType: v4.00+')
lines.append('PlayResX: 1920')
lines.append('PlayResY: 1080')
lines.append('WrapStyle: 0')
lines.append('ScaledBorderAndShadow: yes')
lines.append('')
lines.append('[V4+ Styles]')
lines.append('Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding')
lines.append('Style: Sub,Noto Sans SC,46,&H00F4FFEA,&H00FFFFFF,&H00143028,&H8C14243C,0,0,0,0,100,100,0.5,0,3,8,0,2,120,120,64,1')
lines.append('Style: Note,Noto Sans SC,33,&H00FFF0C8,&H00FFFFFF,&H00143028,&H8C14243C,1,0,0,0,100,100,0.5,0,3,6,0,2,120,120,26,1')
lines.append('Style: Title,Noto Sans SC,96,&H00FFFFFF,&H00FFFFFF,&H008C2E1A10,&H96000000,1,0,0,0,100,100,2,0,1,4,2,8,80,80,0,1')
lines.append('')
lines.append('[Events]')
lines.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')

for i, (src, ip, dur, vo) in enumerate(PLAN):
    st = starts[i] + 0.35
    en = starts[i] + dur - 0.15
    for j, t in enumerate(TEXTS[vo]):
        lines.append(f'Dialogue: 0,{ass_time(st)},{ass_time(en)},Sub,,0,0,0,,{t}')
    if vo in NAME_NOTE:
        lines.append(f'Dialogue: 1,{ass_time(st)},{ass_time(en)},Note,,0,0,0,,{NAME_NOTE[vo]}')

# title overlay
t_st, t_dur, t_text = TITLE_AT
lines.append(f'Dialogue: 2,{ass_time(t_st+0.3)},{ass_time(t_st+t_dur-0.3)},Title,,0,0,0,,{{\\fad(450,450)}}{t_text}')
with open(f'{TMP}/subs.ass', 'w') as f:
    f.write('\n'.join(lines) + '\n')
print('subs ok')

# 4. audio mix
fc = []
mix_ins = []
for i, (src, ip, dur, vo) in enumerate(PLAN):
    delay_ms = int((starts[i] + 0.35) * 1000)
    fc.append(f'[{i+1}:a]aresample=44100,adelay={delay_ms}|{delay_ms}[a{i}]')
    mix_ins.append(f'[a{i}]')
bgm_idx = len(PLAN) + 1
fc.append(f'[{bgm_idx}:a]atrim=0:{total},aresample=44100,volume=0.55,afade=t=in:d=1.5,afade=t=out:st={total-2.6:.2f}:d=2.6[bgm]')
mix_ins.append('[bgm]')
fc.append(f'{"".join(mix_ins)}amix=inputs={len(mix_ins)}:duration=longest:normalize=0,volume=1.0,alimiter=limit=0.95[aout]')
cmd = ['ffmpeg', '-y', '-loglevel', 'error',
       '-i', f'{TMP}/silent.mp4']
for _, _, _, vo in PLAN:
    cmd += ['-i', f'{VO}/{vo}']
cmd += ['-i', '/home/z/my-project/download/audio/bgm.wav']
cmd += ['-filter_complex', ';'.join(fc), '-map', '0:v', '-map', '[aout]',
        '-vf', f'ass={TMP}/subs.ass:fontsdir=/usr/share/fonts',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', FINAL]
subprocess.run(cmd, check=True)
print('FINAL OK', FINAL, round(vdur(FINAL), 2), os.path.getsize(FINAL))
