#!/usr/bin/env python3
"""Build the intro / end cards for the promo video (1920x1080, factual only)."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (24, 29, 40)
PANEL = (34, 40, 54)
GREEN = (120, 200, 130)
PURPLE = (150, 120, 190)
GREY = (150, 158, 170)
WHITE = (232, 236, 241)

NOTO = '/usr/share/fonts/truetype/chinese/NotoSansSC-'
DEJAVU = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
DEJAVU_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def f(path, size):
    return ImageFont.truetype(path, size)


def base():
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    # subtle side accent line
    d.rectangle((0, 0, 14, H), fill=(46, 52, 70))
    return im, d


def center(d, y, text, font, fill):
    bb = d.textbbox((0, 0), text, font=font)
    d.text(((W - bb[2] + bb[0]) / 2, y), text, font=font, fill=fill)


# ---------------- intro ----------------
im, d = base()
center(d, 250, 'OPEN SOURCE · 真 实 录 屏', f(NOTO + 'Regular.ttf', 34), GREY)

center(d, 350, 'Algorithm Competition Assistant', f(DEJAVU_B, 86), WHITE)
center(d, 480, 'Sublime Text 4 算法竞赛本地判题插件 · FastOlympicCoding 优化版',
       f(NOTO + 'Regular.ttf', 40), GREY)

# demo strip
d.rounded_rectangle((410, 600, 1510, 700), 16, fill=PANEL)
center(d, 626, '实战演示：CSP-S 2026 第二轮 T1 能量水晶 (crystal)',
       f(NOTO + 'Bold.ttf', 42), GREEN)
center(d, 790, '一键导入题目  →  底部完成正解  →  Ctrl+Alt+B 本地判题',
       f(NOTO + 'Regular.ttf', 34), WHITE)

center(d, 950, 'github.com/chenmoulaile/algorithm-competition-assistant',
       f(DEJAVU, 30), PURPLE)
center(d, 1010, 'v3.0.7 · MIT License · DejaVu Sans Mono',
       f(DEJAVU, 24), GREY)
im.save('/tmp/card_intro.png')

# ---------------- end card ----------------
im, d = base()
center(d, 200, '本 场 判 题 结 果', f(NOTO + 'Regular.ttf', 32), GREY)

d.rounded_rectangle((560, 270, 1360, 400), 18, fill=PANEL)
center(d, 300, '2 / 2  AC', f(DEJAVU_B, 72), GREEN)
center(d, 428, '测试 1 · 10 ms · 1 MB      测试 2 · 7 ms · 0 MB      总用时 0.03 s',
       f(NOTO + 'Regular.ttf', 30), WHITE)

feats = [
    'Competitive Companion / URL 一键抓题导入',
    '本地判题：AC · WA · TLE · MLE · RE · PE',
    '文件 IO 模式（NOI / CSP-S freopen）· 对拍压力测试',
    '详情页：输入 / 预期 / 实际 / 逐行 diff',
]
y = 530
for t in feats:
    d.ellipse((470, y + 14, 486, y + 30), fill=GREEN)
    d.text((510, y), t, font=f(NOTO + 'Regular.ttf', 32), fill=WHITE)
    y += 62

center(d, 810, '全部画面均为真实录屏 · Sublime Text 4 (build 4215) + Algorithm Competition Assistant 3.0.7',
       f(NOTO + 'Regular.ttf', 26), GREY)
center(d, 860, '题目与样例：洛谷 P17831 [CSP-S 2026] 能量水晶 crystal（官方样例 #1 / #2）',
       f(NOTO + 'Regular.ttf', 26), GREY)

center(d, 940, 'github.com/chenmoulaile/algorithm-competition-assistant',
       f(DEJAVU_B, 36), PURPLE)
center(d, 1010, 'MIT License · 感谢观看', f(NOTO + 'Regular.ttf', 26), GREY)
im.save('/tmp/card_end.png')
print('cards saved')
