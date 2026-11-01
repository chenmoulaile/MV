#!/usr/bin/env python3
"""生成 11 段中文配音（edge-tts，Yunxi 神经语音）。"""
import asyncio
import os
import sys
import edge_tts

DIR = '/home/z/my-project/download/audio'
os.makedirs(DIR, exist_ok=True)

VOICE = 'zh-CN-YunxiNeural'
RATE = '+4%'

SEGMENTS = [
    ('vo01', '算法竞赛，你需要一个更顺手的搭档。'),
    ('vo02', 'CSP-S 2026 第一题，能量水晶。洛谷 P17831，真实赛题，真实页面。'),
    ('vo03', '装好 Competitive Companion，轻轻一点。'),
    ('vo04', '源文件自动建好，样例、时限、内存限制，全部就位。'),
    ('vo05', '算法贴到文件末尾，四十行，一气呵成。'),
    ('vo06', 'Ctrl Alt B，编译运行，两组样例同时判定。'),
    ('vo07', 'AC。七毫秒，十五毫秒，时间与内存，一目了然。'),
    ('vo08', '点开详情：输入、期望、实际、逐行比对，全部对齐。'),
    ('vo09', '一条命令，切换英文界面。'),
    ('vo10', '同一份代码，两种语言，一样的利落。'),
    ('vo11', 'Algorithm Competition Assistant，MIT 开源，一键安装。把时间留给算法本身。'),
]


async def gen(name, text):
    mp3 = os.path.join(DIR, name + '.mp3')
    wav = os.path.join(DIR, name + '.wav')
    c = edge_tts.Communicate(text, VOICE, rate=RATE)
    await c.save(mp3)
    # 统一转 48k wav 方便后期
    os.system('ffmpeg -y -v quiet -i "%s" -ar 48000 -ac 2 "%s"' % (mp3, wav))
    dur = os.popen(
        'ffprobe -v quiet -show_entries format=duration -of csv=p=0 "%s"'
        % wav).read().strip()
    print(name, dur)
    return dur


async def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    for name, text in SEGMENTS:
        if only and name not in only:
            continue
        await gen(name, text)


asyncio.run(main())
print('ALL_DONE')
